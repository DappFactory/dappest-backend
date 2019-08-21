import os
from datetime import datetime, timedelta
from time import sleep
from decimal import Decimal
from numpy import array, log, argsort
from celery.exceptions import SoftTimeLimitExceeded
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from sqlalchemy.orm import noload
from web3 import Web3

import dapp_store_backend.models as models
from dapp_store_backend.settings import DevConfig, ProdConfig
from dapp_store_backend.enums.categories import DappCategory
from dapp_store_backend.api.v1.public.dapp import ListDapps
from dapp_store_backend.schemas.blockchain_schema import BlockchainSchema
from dapp_store_backend.schemas.block_interval_schema import BlockIntervalSchema
from dapp_store_backend.schemas.review_schema import ReviewSchema
from dapp_store_backend.schemas.dapp_list_address_schema import DappListAddressSchema
from dapp_store_backend.app import celery
from dapp_store_backend.extensions import db
from dapp_store_backend.worker.services.etherscan import Etherscan
from dapp_store_backend.worker.services.infura import Infura
from dapp_store_backend.worker.services.utilities import combine_dict_same_keys, extract_uvt_from_transactions, extract_vt_from_transactions, wrap_result
from dapp_store_backend.utilities import round_down_datetime
from .constants import Metric, Network


if os.environ.get("DAPP_STORE_BACKEND_ENV") == 'prod':
    config = ProdConfig
else:
    config = DevConfig

# Initialize 3rd-party API wrappers
etherscan = Etherscan(config.ETHERSCAN_API_KEY)
infura = Infura(config.INFURA_API_KEY, Network.mainnet)


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Setup the periodic tasks:
        1. Add first and last block of each day into database.
        2. Check if dapp statistics available for previous day.
        3. If not present, get the dapp statistics for previous day.
    """
    sender.add_periodic_task(config.PERIODIC_TASK_TIME, update_periodic_dapp_stats.s())


@celery.task(name='add_blockchain_task')
def add_blockchain_task(name, symbol):

    blockchain = models.Blockchain(name=name, symbol=symbol)
    blockchain.save()


@celery.task(name='update_periodic_dapp_stats')
def update_periodic_dapp_stats():
    """
    Wrapper for chained task to update block interval and get dapp stats from latest complete block interval.
    """
    return (update_block_day.s() | get_dapp_metrics.s() | add_dapp_metrics.s() | calculate_dapp_ranking.si()
            | set_dapp_of_the_day.si() | set_review_of_the_day.si()).delay()


@celery.task(name='update_contract_deployment_date')
def update_contract_deployment_date(dapp_submission_id, contracts):
    """
    Wrapper for chained task to get contract deployment date and update dapp submission date
    :param dapp_submission_id:
    :param contracts:
    :return:
    """
    return (get_contract_deployment_date.s(contracts) | add_contract_deployment_date.s(dapp_submission_id)).delay()


@celery.task(name='add_review_with_metrics')
def add_review_with_metrics(user_address, contract_addresses, user_id, review_json):
    """
    Add reivew with metrics.
    :return:
    """
    return (get_eth_volume_and_transactions.s(user_address, contract_addresses) | add_review.s(user_id, review_json)).delay()


@celery.task(name='get_contract_deployment_date')
def get_contract_deployment_date(contracts):
    """
    Function to get contract(s)' deployment date from their
    first transaction.

    :param contracts:
    :return:
    """
    # initialize list to store all deployment dates 1-1 with len(contracts)
    deployment_dates = []

    if contracts:
        # go through each of the contracts
        for contract in contracts:
            try:
                transactions = etherscan.get_transactions(contract, 0, 99999999)

                if transactions:
                    # get the first transaction
                    inception_date = int(transactions[0].get('timeStamp'))

                    if inception_date:
                        deployment_dates.append(inception_date)
            except Exception:
                print(f'Error gettings transactions for address: {contract}')
                pass

    return min(deployment_dates) if deployment_dates else None


@celery.task(name='add_contract_deployment_date')
def add_contract_deployment_date(deployment_date, dapp_submission_id):
    """
    Update launch date for submitted dapp
    :param dapp_submission_id:
    :param deployment_date:
    :return:
    """

    dapp_submission = models.DappSubmission.get_by_id(dapp_submission_id)

    if dapp_submission and deployment_date:
        dapp_submission.launch_date = datetime.utcfromtimestamp(deployment_date)
        dapp_submission.save()
        return {'message': 'SUCCESS'}

    return {'message': 'Failed to update dapp submission launch date.'}


@celery.task(name='update_block_day')
def update_block_day():
    """
    Adds the first and last block of the day.
    """
    rounded_time = int(round_down_datetime(datetime.utcnow(), unit=config.BLOCK_INTERVAL_UNIT).timestamp())

    blockchain_schema = BlockchainSchema(many=True)
    results = models.Blockchain.query.all()
    blockchains = blockchain_schema.dump(results).data

    block_interval_schema = BlockIntervalSchema()
    block_intervals = {}

    for blkchain in blockchains:

        blockchain_id = blkchain.get('id')
        symbol = blkchain.get('symbol')

        # TODO: remove once conditional implemented for every blockchain
        completed_block_interval = {}

        if symbol == 'ETH':
            block_start = get_start_block_eth(rounded_time).get('result')

            current_block_interval_results = models.BlockInterval.query.options(noload('*'))\
                .filter_by(blockchain_id=blockchain_id,
                           time_start=rounded_time).first()
            current_block_interval = block_interval_schema.dump(current_block_interval_results).data

            last_block_interval_results = models.BlockInterval.query.options(noload('*')) \
                .filter_by(blockchain_id=blockchain_id,
                           time_start=rounded_time - config.FETCHER_BLOCK_INTERVAL).first()
            last_block_interval = block_interval_schema.dump(last_block_interval_results).data

            if last_block_interval.get('time_stop') == rounded_time:
                block_interval = models.BlockInterval.query.get(last_block_interval.get('id'))

                if not block_interval or not block_start:
                    return {}

                if not block_interval.block_start:
                    block_interval.block_start = 0

                if not block_interval.block_stop:
                    assert (
                            block_start > block_interval.block_start), 'Stop block must be greater than start block.'
                    block_interval.block_stop = block_start

                db.session.commit()
                block_interval_schema = BlockIntervalSchema()
                completed_block_interval = block_interval_schema.dump(block_interval).data
                print('COMPLETED', completed_block_interval)

            if not current_block_interval:
                try:
                    block_interval = models.BlockInterval(blockchain_id=blockchain_id,
                                                          time_start=rounded_time,
                                                          time_stop=rounded_time + config.FETCHER_BLOCK_INTERVAL,
                                                          block_start=block_start)
                    block_interval.save()

                except IntegrityError as e:
                    db.session().rollback()
                    return {'Error': '({}, {}) already exists.'.format(blockchain_id, rounded_time)}

        elif symbol == 'NEO':
            completed_block_interval = {}

        block_intervals[symbol] = completed_block_interval

    print(block_intervals)
    return block_intervals


@celery.task(name='get_dapp_metrics')
def get_dapp_metrics(block_interval_dict):
    """
    Get all dapp metrics for a specific block interval.
    """
    dapp_results = {'metrics': []}

    if not any(block_interval_dict.get(x) for x in block_interval_dict):
        return dapp_results

    # TODO: add check for existing dapp metrics and skip if exists
    dapp_list_address_schema = DappListAddressSchema(many=True)
    results = (models.Dapp.query.join(models.Blockchain).with_entities(models.Dapp.id, models.Blockchain.symbol,
                                                                       models.Dapp.address).all())
    dapps = dapp_list_address_schema.dump(results).data

    for dapp in dapps:

        id = dapp.get('id')
        symbol = dapp.get('symbol')
        address = dapp.get('address')

        block_interval = block_interval_dict.get(symbol)
        block_start = block_interval.get('block_start')
        block_stop = block_interval.get('block_stop')
        block_interval_id = block_interval.get('id')

        if not block_start or not block_stop:
            continue

        results = {}
        results['dapp_id'] = id

        if symbol == 'ETH':
            results['metrics'] = get_users_volume_transactions(
                address, block_start, block_stop - 1).get('result')

            results['block_interval_id'] = block_interval_id

        dapp_results['metrics'].append(results)

        sleep(0.5)

    return dapp_results


@celery.task(name='get_start_block_eth')
def get_start_block_eth(epoch_time=None):
    """
    Get first ethereum block for a specific epoch time.
    Epoch time must be within 300 seconds of latest block time.
    """
    if not epoch_time:
        epoch_time = int(datetime.utcnow().timestamp())

    print('EPOCH TIME: {}'.format(epoch_time))
    latest_block_info = infura.get_block_by_number('latest')

    latest_block_time = int(latest_block_info.get('timestamp'), 16)
    latest_block_number = int(latest_block_info.get('number'), 16)

    if abs(epoch_time - latest_block_time) > 300:
        return {'state': 0, 'message': 'Error: Difference between target time and latest block time > 300s.', 'result': None}

    increment = 1 if (epoch_time > latest_block_time) else -1
    i = 0
    block_number = latest_block_number + increment

    while i < 100:
        print('Block number: {}'.format(block_number))
        block_info = infura.get_block_by_number(block_number)

        if not block_info:
            print('No block info found for block {}'.format(block_number))
            sleep(10)
            continue

        block_time = int(block_info.get('timestamp'), 16)

        if increment == 1 and block_time >= epoch_time:
            print('Found starting block: {}'.format(block_number))
            return wrap_result(block_number)
        elif increment == -1 and block_time < epoch_time:
            print('Found starting block: {}'.format(block_number + 1))
            return wrap_result(block_number + 1)

        block_number += increment
        sleep(0.5)

    return {'state': 0,
            'message': 'Error: Could not find starting block for {t} time after {i} iterations'.format(t=epoch_time, i=i),
            'result': None}


@celery.task(name='get_users_volume_transactions', retry_backoff=2, max_retries=5)
def get_users_volume_transactions(contract_addresses, block_start, block_stop):
    """
    Get the unique users, volume, and number of transactions for multiple
    addresses (single dapp) between block_start and block_stop

    Args:
        contract_addresses (list(str)): Target ethereum addresses
        block_start (int): Start block
        block_stop (int): End block
    """
    result = {
        Metric.users.name: [],
        Metric.volume.name: 0,
        Metric.transactions.name: 0
    }

    try:
        for address in contract_addresses:
            result = combine_dict_same_keys(result, etherscan.process_transactions(
                lambda x: extract_uvt_from_transactions(x, address), address,
                block_start, block_stop))

            sleep(0.5)

        result[Metric.users.name] = len(set(result.get(Metric.users.name)))
        return wrap_result(result)
    except SoftTimeLimitExceeded:
        print('Error: SoftTimeLimitExceeded.')
        return wrap_result(None)


@celery.task(name='get_eth_volume_and_transactions', retry_backoff=2, max_retries=5)
def get_eth_volume_and_transactions(user_address, contract_addresses):
    """
    Get the volume and number of transactions between user address
    and contract addressses.
    """
    # TODO: consider creating table in DB to track tasks
    try:
        result = etherscan.process_transactions(
            lambda x: extract_vt_from_transactions(
                x, user_address, contract_addresses),
            user_address, 0, 99999999)

        return wrap_result(result)
    except SoftTimeLimitExceeded:
        print('Error: SoftTimeLimitExceeded.')
        return wrap_result(None)


@celery.task(name='calculate_dapp_ranking')
def calculate_dapp_ranking():
    """
    Calculate dapp ranking for all dapps
    :return:
    """
    dapps = ListDapps.get_dapps(category=DappCategory.ALL.name)

    # Get block interval
    # TODO: get latest block interval for all blockchains
    time_start = (int(round_down_datetime(
        datetime.utcnow(), unit=config.BLOCK_INTERVAL_UNIT).timestamp()) -
                  config.BLOCK_INTERVAL_SECONDS * 5)

    block_interval_first = (db.session.query(func.min(models.BlockInterval.id))
                            .filter(models.BlockInterval.time_start >= time_start).subquery())

    metric_latest = (db.session.query(models.Metric.dapp_id,
                                      func.max(models.Metric.block_interval_id).label('latest_block_interval'))
                     .filter(models.Metric.block_interval_id >= block_interval_first)
                     .group_by(models.Metric.dapp_id)
                     .first())

    if metric_latest is None:
        print('Latest metrics does not exist.')
        return {'status': 'FAILURE'}

    mat = array([[x.get('rating'), x.get('rating_count') if x.get('rating_count') <= config.MAX_REVIEW_COUNT else config.MAX_REVIEW_COUNT,
                  log(x.get('metrics').get('users') + 1),
                  float(Decimal(Web3.fromWei(x.get('metrics').get('volume'), 'ether') + 1).ln()),
                  log(x.get('metrics').get('transactions') + 1)] for x in dapps])

    max_users = max(mat[:, 2])
    max_users = max_users if max_users > 0 else 1
    max_volume = max(mat[:, 3])
    max_volume = max_volume if max_volume > 0 else 1
    max_transactions = max(mat[:, 4])
    max_transactions = max_transactions if max_transactions > 0 else 1

    weights = [((x[0] / 5) * (x[1] / config.MAX_REVIEW_COUNT) * config.RATING_WEIGHT) +
               ((x[2] / max_users) * config.USER_WEIGHT +
                (x[3] / max_volume) * config.VOLUME_WEIGHT +
                (x[4] / max_transactions) * config.TRANSACTION_WEIGHT) for x in mat]

    ranking_idx = list(reversed(argsort(weights)))
    rankings = {x: [] for x in [c.name for c in DappCategory]}
    ranking_count = {x: 1 for x in [c.name for c in DappCategory]}

    for i, idx in enumerate(ranking_idx):
        current_dapp = dapps[idx]
        dapp_id = current_dapp.get('id')
        category = current_dapp.get('category').replace(' ', '_').upper()

        if i < config.MAX_RANKING:
            all_ranking = models.Ranking(dapp_id=dapp_id, block_interval_id=metric_latest.latest_block_interval,
                                         ranking_name_id=DappCategory.ALL.value,
                                         rank=ranking_count[DappCategory.ALL.name])
            db.session.add(all_ranking)
            ranking_count[DappCategory.ALL.name] += 1

        if len(rankings[category]) < config.MAX_RANKING:
            # TODO: get ranking_name id from database instead of enum
            category_ranking = models.Ranking(dapp_id=dapp_id, block_interval_id=metric_latest.latest_block_interval,
                                              ranking_name_id=DappCategory[category].value,
                                              rank=ranking_count[category])
            db.session.add(category_ranking)
            ranking_count[category] += 1

    db.session.commit()

    return {'status': 'SUCCESS'}


@celery.task(name='add_dapp_metrics')
def add_dapp_metrics(dapp_metrics_dict):
    """
    Insert dapp metrics into db.
    """
    metrics = dapp_metrics_dict.get('metrics')

    if metrics:
        for dapp_metrics in metrics:
            metric = models.Metric(dapp_id=dapp_metrics.get('dapp_id'),
                                   block_interval_id=dapp_metrics.get('block_interval_id'),
                                   data=dapp_metrics.get('metrics'))

            db.session.add(metric)

        try:
            db.session.commit()
        except IntegrityError as e:
            db.session().rollback()
            print(
                'Metric already exists for specified block_interval, rolling back batch of metrics.')
            return {'status': 'FAILED'}

    return {'status': 'SUCCESS'}


@celery.task(name='add_review')
def add_review(metrics_result, user_id, request_json):
    """
    Add review with metrics, user id, and request json.
    :param metrics_result:
    :param user_id:
    :param request_json:
    :return:
    """
    verified = False
    metrics = metrics_result.get('result')

    if metrics:
        in_volume = metrics.get('in_volume')
        out_volume = metrics.get('out_volume')
        transactions = metrics.get('transactions')

        metrics['in_volume'] = float(Decimal(Web3.fromWei(in_volume, 'ether'))) if in_volume else 0
        metrics['out_volume'] = float(Decimal(Web3.fromWei(out_volume, 'ether'))) if in_volume else 0

        if (transactions > config.VERIFIED_USER_MIN_TRANSACTIONS_THRESHOLD and metrics['out_volume'] >
                config.VERIFIED_USER_MIN_OUT_VOLUME_THRESHOLD):
            verified = True

    subitted_review = models.Review(dapp_id=request_json.get('dapp_id'),
                                    user_id=user_id,
                                    rating=request_json.get('rating'),
                                    title=request_json.get('title'),
                                    review=request_json.get('review'),
                                    feature=request_json.get('feature'),
                                    data=metrics,
                                    verified=verified)
    subitted_review.save()

    review_schema = ReviewSchema()
    serialized = review_schema.dump(subitted_review).data

    return serialized


@celery.task(name='set_dapp_of_the_day')
def set_dapp_of_the_day():
    """
    Set dapp of the day.
    :return:
    """

    try:
        latest_time = db.session.query(func.max(models.Dapp.uploaded_at).label('max_datetime')).one()

        if not latest_time:
            return {'status': 'Could not set dapp of the day. Latest time is empty.'}

        dapp = (db.session.query(models.Dapp.id, func.count(models.Review.id).label('total_reviews'))
                .outerjoin(models.Dapp.reviews).filter((models.Dapp.uploaded_at <= latest_time.max_datetime) &
                                                (models.Dapp.uploaded_at >= latest_time.max_datetime - timedelta(days=3)))
                .group_by(models.Dapp.id).order_by(desc('total_reviews'))
                .first())

        dapp_of_the_day = models.DailyItem.get_by_id(2)
        dapp_of_the_day.item_id = dapp.id
        db.session.commit()

        return {'status': 'SUCCESS'}

    except Exception as e:
        print('EXCEPTION!!!: {}'.format(e))
        return {'Error': 'Could not set dapp of the day.'}


@celery.task(name='set_review_of_the_day')
def set_review_of_the_day():
    """
    Set dapp of the day.
    :return:
    """

    try:
        latest_time = db.session.query(func.max(models.Review.uploaded_at).label('max_datetime')).one()

        if not latest_time:
            return {'status': 'Could not set review of the day. Latest time is empty.'}

        review = (db.session.query(models.Review.id, func.count(models.ReviewLike.id).label('total_likes'))
                  .outerjoin(models.Review.helpful_votes)
                  .filter((models.Review.uploaded_at <= latest_time.max_datetime) &
                          (models.Review.uploaded_at >= latest_time.max_datetime - timedelta(days=1)))
                  .group_by(models.Review.id).order_by(desc('total_likes'))
                  .first())

        review_of_the_day = models.DailyItem.get_by_id(1)
        review_of_the_day.item_id = review.id
        db.session.commit()

        return {'status': 'SUCCESS'}

    except Exception as e:
        print('ERROR!!!: {}'.format(e))
        return {'status': 'FAILED'}

