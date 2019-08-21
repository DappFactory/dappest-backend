# -*- coding: utf-8 -*-
"""Public endpoints for Dapps."""
from datetime import datetime
from flask import request, current_app
from flask_restplus import Namespace, Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from uuid import uuid4
from sqlalchemy.sql import func
from sqlalchemy.orm import subqueryload
from sqlalchemy.util import KeyedTuple
from boto3 import client

from dapp_store_backend.extensions import celery
from dapp_store_backend.enums.status import HTTPCodes
from dapp_store_backend.database import db
from dapp_store_backend.settings import Config
from dapp_store_backend.enums.categories import DappCategory
from dapp_store_backend.enums.status import DappSubmissionStatus
from dapp_store_backend.utilities import round_down_datetime
from dapp_store_backend.models.blockchain import Blockchain
from dapp_store_backend.models.featured import Featured
from dapp_store_backend.models.daily_item import DailyItem
from dapp_store_backend.models.ranking_name import RankingName
from dapp_store_backend.models.ranking import Ranking
from dapp_store_backend.models.user import User
from dapp_store_backend.schemas.dapp_schema import DappSchema
from dapp_store_backend.schemas.dapp_list_schema import DappListSchema
from dapp_store_backend.schemas.dapp_submission_schema import DappSubmissionSchema
from dapp_store_backend.schemas.featured_schema import FeaturedSchema
from dapp_store_backend.utilities import (valdate_image_type, upload_image_to_s3, validate_request, verify_eth_address)
from . import Dapp
from . import BlockInterval
from . import Category
from . import Metric
from . import Review
from . import DappSubmission

api = Namespace('dapp', description='Public Dapp endpoints.', path='/public/dapp')


@api.route('/<int:dapp_id>')
class GetDapp(Resource):
    """
    Get all information for single dapp.
    """

    @staticmethod
    def get(dapp_id):
        sort_by = request.args.get('sort')
        reverse = False if request.args.get('order') == 'asc' else True

        dapp_schema = DappSchema(many=False, exclude=['logo_path', 'screenshot'])

        time_start = (int(round_down_datetime(
            datetime.utcnow(), unit=current_app.config['BLOCK_INTERVAL_UNIT']).timestamp())
                      - Config.BLOCK_INTERVAL_SECONDS * 5)

        try:
            block_interval_first = (db.session.query(func.min(BlockInterval.id))
                                    .filter(BlockInterval.time_start >= time_start).subquery())

            metric_latest = (db.session.query(Metric.id, Metric.block_interval_id,
                                              Metric.dapp_id, Metric.data)
                             .filter(Metric.dapp_id == dapp_id, Metric.block_interval_id >= block_interval_first)
                             .order_by(Metric.block_interval_id.desc()).limit(1)
                             .subquery('metric_latest'))

            ranking_latest_block_interval_id = (db.session.query(Ranking.block_interval_id.label('block_interval_latest_id'))
                                                .filter(Ranking.dapp_id == dapp_id, Ranking.block_interval_id >= block_interval_first)
                                                .order_by(Ranking.block_interval_id.desc()).limit(1)
                                                .subquery('ranking_latest_id'))

            ranking_latest = (db.session.query(Ranking.rank, RankingName.name.label('name'))
                              .join(RankingName)
                              .filter(Ranking.dapp_id == dapp_id,
                                      Ranking.block_interval_id == ranking_latest_block_interval_id.c.block_interval_latest_id)
                              .all())

            # TODO: improve query
            result = (Dapp.query.add_columns(metric_latest.c.data.label('metrics'))
                      .outerjoin(metric_latest, metric_latest.c.dapp_id == Dapp.id)
                      .options(subqueryload(Dapp.reviews).subqueryload(Review.user).joinedload(User.reviews))
                      .filter(Dapp.id == dapp_id)
                      .first())

            result[0].rankings = ranking_latest

            if result[1]:
                result[0].metrics = result[1]

            if sort_by in ['rating', 'uploaded_at', 'helpful_count']:
                result[0].reviews.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)

            dapp = dapp_schema.dump(result[0]).data

            return dapp, 200

        except Exception as e:
            print('EXCEPTION!!!!: {}'.format(e))
            return {'Error': 'Failed to retrieve dapp.'}, 404


@api.route('/list')
class ListDapps(Resource):
    """
    Get list of dapps.
    """

    @staticmethod
    def get(selected_category=None):
        category = selected_category.upper() if selected_category is not None else request.args.get('category').upper()
        sort_by = request.args.get('sort')
        reverse = False if request.args.get('order') == 'asc' else True

        if category not in DappCategory.__members__:
            return {}, 404

        try:
            dapps = ListDapps.get_dapps(category, sort_by, reverse)
            return dapps, 200
        except Exception as e:
            print('EXCEPTION!!!!: {}'.format(e))
            return [], 500

    @staticmethod
    def get_dapps(category, sort_by=None, reverse=True):
        time_start = (int(round_down_datetime(
            datetime.utcnow(), unit=current_app.config['BLOCK_INTERVAL_UNIT']).timestamp()) -
                      Config.BLOCK_INTERVAL_SECONDS * 5)

        dapp_list_schema = DappListSchema(many=True)

        try:
            block_interval_first = db.session.query(func.min(BlockInterval.id)) \
                .filter(BlockInterval.time_start >= time_start).subquery()

            metric_latest_block_interval_id = (db.session.query(
                Metric.dapp_id, func.max(Metric.block_interval_id).label('metric_latest_block_interval'))
                                               .filter(Metric.block_interval_id >= block_interval_first)
                                               .group_by(Metric.dapp_id)
                                               .subquery())

            ranking_latest_block_interval_id = (
                db.session.query(Ranking.dapp_id, func.max(Ranking.block_interval_id).label('ranking_latest_block_interval'))
                .filter(Ranking.block_interval_id >= block_interval_first)
                .group_by(Ranking.dapp_id)
                .subquery('ranking_latest_id'))

            ranking_latest = (db.session.query(Ranking.rank, RankingName.name.label('name'),
                                               Ranking.dapp_id, Ranking.block_interval_id)
                              .join(RankingName)
                              .filter(Ranking.block_interval_id == ranking_latest_block_interval_id.c.ranking_latest_block_interval)
                              .distinct()
                              .all())

            ranking_dict = {}
            if ranking_latest:
                for ranking in ranking_latest:
                    ranking_dapp_id = ranking.dapp_id
                    if ranking_dapp_id not in ranking_dict:
                        ranking_dict[ranking_dapp_id] = [ranking]
                    else:
                        ranking_dict[ranking_dapp_id].append(ranking)

                ranking_dict = {k: KeyedTuple([ranking_dict.get(k)], labels=['rankings']) for k in ranking_dict}

            if category == DappCategory.ALL.name:
                # Get average ratings per dapp via subquery
                ratings = Review.query.with_entities(Review.dapp_id, func.avg(Review.rating).label('rating'),
                                                     func.count('*').label('rating_count')) \
                    .group_by(Review.dapp_id).subquery()

                # Get list of all dapps
                results = Dapp.query \
                    .join(Blockchain, Dapp.blockchain_id == Blockchain.id) \
                    .join(Category, Dapp.category_id == Category.id) \
                    .outerjoin(ratings, Dapp.id == ratings.c.dapp_id) \
                    .outerjoin(metric_latest_block_interval_id, Dapp.id == metric_latest_block_interval_id.c.dapp_id) \
                    .outerjoin(Metric, (Dapp.id == Metric.dapp_id) & (
                        Metric.block_interval_id == metric_latest_block_interval_id.c.metric_latest_block_interval)) \
                    .with_entities(Dapp.id, Dapp.name, Dapp.url, Dapp.uploaded_at, Dapp.tagline, Dapp.description,
                                   Dapp.logo_path, Category.name.label('category'), Blockchain.symbol.label('blockchain'),
                                   ratings.c.rating, ratings.c.rating_count, Metric.data.label('metrics')) \
                    .all()

            else:
                category = ' '.join([x.capitalize() for x in category.split('_')])

                # Get average ratings per dapp in the category via subquery
                ratings = Review.query \
                    .join(Dapp).join(Category) \
                    .filter(Category.name == category) \
                    .with_entities(Review.dapp_id, func.avg(Review.rating).label('rating'),
                                   func.count('*').label('rating_count')) \
                    .group_by(Review.dapp_id).subquery()

                # Get list of dapps in specific category
                results = Dapp.query \
                    .join(Blockchain, Dapp.blockchain_id == Blockchain.id) \
                    .join(Category, Dapp.category_id == Category.id) \
                    .outerjoin(ratings, Dapp.id == ratings.c.dapp_id) \
                    .outerjoin(metric_latest_block_interval_id, Dapp.id == metric_latest_block_interval_id.c.dapp_id) \
                    .outerjoin(Metric, (Dapp.id == Metric.dapp_id) & (
                        Metric.block_interval_id == metric_latest_block_interval_id.c.metric_latest_block_interval)) \
                    .filter(Category.name == category) \
                    .with_entities(Dapp.id, Dapp.name, Dapp.url, Dapp.uploaded_at, Dapp.tagline, Dapp.description,
                                   Dapp.logo_path, Category.name.label('category'), Blockchain.symbol.label('blockchain'),
                                   ratings.c.rating, ratings.c.rating_count, Metric.data.label('metrics')) \
                    .all()

            if ranking_dict:
                for i, r in enumerate(results):
                    ranking_tuple = ranking_dict.get(r.id)
                    results[i] = KeyedTuple(r + ranking_tuple, r.keys() + ranking_tuple.keys())

            dapps = dapp_list_schema.dump(results).data

            if sort_by in ['users', 'volume', 'transactions']:
                dapps.sort(key=lambda x: x['metrics'].get(sort_by), reverse=reverse)
            elif sort_by in ['rating', 'name', 'uploaded_at']:
                dapps.sort(key=lambda x: x.get(sort_by), reverse=reverse)

            return dapps
        except Exception as e:
            print('EXCEPTION!!!!: {}'.format(e))
            raise e

    @staticmethod
    def get_selected_dapps(dapp_id_list):

        if not dapp_id_list:
            return [], 200

        time_start = (int(round_down_datetime(
            datetime.utcnow(), unit=current_app.config['BLOCK_INTERVAL_UNIT']).timestamp()) -
                      Config.BLOCK_INTERVAL_SECONDS * 5)

        dapp_list_schema = DappListSchema(many=True)

        try:
            block_interval_first = db.session.query(func.min(BlockInterval.id)) \
                .filter(BlockInterval.time_start >= time_start).subquery()

            metric_latest_block_interval_id = (db.session.query(
                Metric.dapp_id, func.max(Metric.block_interval_id).label('metric_latest_block_interval'))
                                               .filter(Metric.block_interval_id >= block_interval_first)
                                               .filter(Metric.dapp_id.in_(dapp_id_list))
                                               .group_by(Metric.dapp_id)
                                               .subquery())

            # Get average ratings per dapp via subquery
            ratings = (Review.query.filter(Review.dapp_id.in_(dapp_id_list))
                       .with_entities(Review.dapp_id, func.avg(Review.rating).label('rating'),
                                      func.count('*').label('rating_count'))
                       .group_by(Review.dapp_id).subquery())

            # Get list of all dapps
            results = Dapp.query \
                .join(Blockchain, Dapp.blockchain_id == Blockchain.id) \
                .join(Category, Dapp.category_id == Category.id) \
                .outerjoin(ratings, Dapp.id == ratings.c.dapp_id) \
                .outerjoin(metric_latest_block_interval_id,
                           Dapp.id == metric_latest_block_interval_id.c.dapp_id) \
                .outerjoin(Metric, (Dapp.id == Metric.dapp_id) & (
                    Metric.block_interval_id == metric_latest_block_interval_id.c.metric_latest_block_interval)) \
                .filter(Dapp.id.in_(dapp_id_list)) \
                .with_entities(Dapp.id, Dapp.name, Dapp.url, Dapp.uploaded_at, Dapp.tagline, Dapp.description,
                               Dapp.logo_path, Category.name.label('category'),
                               Blockchain.symbol.label('blockchain'),
                               ratings.c.rating, ratings.c.rating_count, Metric.data.label('metrics')) \
                .all()

            dapps = dapp_list_schema.dump(results).data

            return dapps
        except Exception as e:
            print('EXCEPTION!!!!: {}'.format(e))
            raise e


@api.route('/submit')
class SubmitDapp(Resource):
    """
    Add dapp to submission list.
    """

    @staticmethod
    def post():
        try:
            request_json = request.get_json()
            current_user = get_jwt_identity()
            user_address = request_json.get('user_address')

            if current_user:
                user = User.get_user_from_jwt_token(current_user)

                if not user:
                    return {'Error': 'Invalid token'}, 400

            elif user_address:
                if not verify_eth_address(user_address):
                    return {'Error': 'Ethereum address not valid.'}, 400

                user = User.query.filter_by(address=user_address).first()

                s3_id = str(uuid4())

                if not user:
                    user = User(address=user_address,
                                username=user_address,
                                blockchain_id=1,
                                s3_id=s3_id)
                    user.save()
            else:
                return {'Error': 'Invalid user address'}, 400

            if not validate_request(request_json, ['name', 'url', 'address', 'blockchain', 'category', 'author',
                                                   'email', 'logo', 'screenshots', 'tagline', 'description']):
                return {'Error': 'Missing required field.'}, 400

            logo = request_json.get('logo')
            screenshots = request_json.get('screenshots')
            logo_base64_string = logo.get('image')
            logo_file_type = logo.get('file_type')
            address = request_json.get('address')

            # Validate contract addresses
            if any(verify_eth_address(x) for x in address):
                return {'Error': 'Ethereum contract address not valid.'}, 400

            # Validate logo
            logo_file_type = logo_file_type.lower() if logo_file_type else None
            logo_error = valdate_image_type(logo_base64_string, logo_file_type)
            if logo_error:
                return {'Logo Error': logo_error}, 400

            # Validate max number of screenshots
            if len(screenshots) > 5:
                return {'Error': 'Max number of screenshots allowed is 5.'}, 400

            # Validate screenshots
            for s in screenshots:
                base64_string = s.get('image')
                file_type = s.get('file_type')
                file_type = file_type.lower() if file_type else None

                error = valdate_image_type(base64_string, file_type)
                if error:
                    return {'Error': error}, 400

            s3_client = client('s3',
                               aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                               aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'])
            bucket = current_app.config['S3_BUCKET_NAME']

            # Upload image to S3
            s3_id = str(uuid4())

            try:
                logo_path = upload_image_to_s3(s3_client, bucket, logo_base64_string, logo_file_type,
                                               path=f'dapp_submission/{s3_id}/logo')
            except Exception:
                return {'Error': 'Failed to upload image to S3.'}, 500

            # Upload screenshots to S3
            screenshot_names = []
            try:
                for s in screenshots:
                    base64_string = s.get('image')
                    file_type = s.get('file_type')
                    file_type = file_type.lower() if file_type else None
                    screenshot_name = upload_image_to_s3(s3_client, bucket, base64_string, file_type,
                                                         path=f'dapp_submission/{s3_id}/screenshots')
                    screenshot_names.append(screenshot_name)
            except Exception:
                return {'Error': 'Failed to upload image to S3.'}, 500

            dapp_submission = DappSubmission(name=request_json.get('name'),
                                             url=request_json.get('url'),
                                             address=request_json.get('address'),
                                             blockchain_id=request_json.get('blockchain'),
                                             category_id=request_json.get('category'),
                                             user_id=user.id,
                                             author=request_json.get('author'),
                                             email=request_json.get('email'),
                                             logo_path=logo_path,
                                             screenshot=screenshot_names,
                                             tagline=request_json.get('tagline'),
                                             description=request_json.get('description'),
                                             whitepaper=request_json.get('whitepaper'),
                                             social_media=request_json.get('social_media'),
                                             s3_id=s3_id,
                                             status=DappSubmissionStatus.SUBMITTED.value)
            dapp_submission.save()

            celery.send_task('update_contract_deployment_date', (dapp_submission.id, address))

            dapp_submission_schema = DappSubmissionSchema()
            result = dapp_submission_schema.dump(dapp_submission).data
            return result, 200

        except Exception as e:
            return {'Error': 'Failed to submit dapp: {}.'.format(e)}, 500


@api.route('/submit/prelaunch')
class SubmitDappPrelaunch(Resource):
    """
    Add dapp to submission list prelaunch.
    """

    @staticmethod
    def post():
        try:
            request_json = request.get_json()
            if not validate_request(request_json, ['name', 'url', 'address', 'user_address', 'blockchain', 'category',
                                                   'author', 'email', 'logo', 'screenshots', 'tagline',
                                                   'description']):
                return {'Error': 'Missing required field.'}, 400

            logo = request_json.get('logo')
            screenshots = request_json.get('screenshots')
            logo_base64_string = logo.get('image')
            logo_file_type = logo.get('file_type')
            address = request_json.get('address')

            # Validate logo
            logo_file_type = logo_file_type.lower() if logo_file_type else None
            logo_error = valdate_image_type(logo_base64_string, logo_file_type)
            if logo_error:
                return {'Logo Error': logo_error}, 400

            # Validate max number of screenshots
            if len(screenshots) > 5:
                return {'Error': 'Max number of screenshots allowed is 5.'}, 400

            # Validate screenshots
            for s in screenshots:
                base64_string = s.get('image')
                file_type = s.get('file_type')
                file_type = file_type.lower() if file_type else None

                error = valdate_image_type(base64_string, file_type)
                if error:
                    return {'Error': error}, 400

            s3_client = client('s3',
                               aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                               aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'])
            bucket = current_app.config['S3_BUCKET_NAME']

            # Create user
            user_address = request_json.get('user_address')

            if not verify_eth_address(user_address):
                return {'Error': 'Ethereum address not valid.'}, 400

            user = User.query.filter_by(address=user_address).first()
            # Upload image to S3
            s3_id = str(uuid4())

            if not user:
                user = User(address=user_address,
                            username=user_address,
                            blockchain_id=1,
                            s3_id=s3_id)
                user.save()

            # Upload image to S3
            s3_id = str(uuid4())

            try:
                logo_path = upload_image_to_s3(s3_client, bucket, logo_base64_string, logo_file_type,
                                               path=f'dapp_submission/{s3_id}/logo')
            except Exception:
                return {'Error': 'Failed to upload image to S3.'}, 500

            # Upload screenshots to S3
            screenshot_names = []
            try:
                for s in screenshots:
                    base64_string = s.get('image')
                    file_type = s.get('file_type')
                    file_type = file_type.lower() if file_type else None
                    screenshot_name = upload_image_to_s3(s3_client, bucket, base64_string, file_type,
                                                         path=f'dapp_submission/{s3_id}/screenshots')
                    screenshot_names.append(screenshot_name)
            except Exception:
                return {'Error': 'Failed to upload image to S3.'}, 500

            dapp_submission = DappSubmission(name=request_json.get('name'),
                                             url=request_json.get('url'),
                                             address=address,
                                             blockchain_id=request_json.get('blockchain'),
                                             category_id=request_json.get('category'),
                                             user_id=user.id,
                                             author=request_json.get('author'),
                                             email=request_json.get('email'),
                                             logo_path=logo_path,
                                             screenshot=screenshot_names,
                                             tagline=request_json.get('tagline'),
                                             description=request_json.get('description'),
                                             whitepaper=request_json.get('whitepaper'),
                                             social_media=request_json.get('social_media'),
                                             s3_id=s3_id,
                                             status=DappSubmissionStatus.SUBMITTED.value)
            dapp_submission.save()

            #celery.send_task('update_contract_deployment_date', (dapp_submission.id, address))

            dapp_submission_schema = DappSubmissionSchema()
            result = dapp_submission_schema.dump(dapp_submission).data
            return result, 200

        except Exception as e:
            return {'Error': 'Failed to submit dapp: {}.'.format(e)}, 500


# TODO: reformat endpoint
# TODO: add sorting by similarity of match, limit number of search results
@api.route('/search')
class Search(Resource):
    """
    Search by dapp name.
    """

    @staticmethod
    def get():
        name = request.args.get('name')

        if not name:
            return [], 200

        time_start = (int(round_down_datetime(
            datetime.utcnow(), unit=current_app.config['BLOCK_INTERVAL_UNIT']).timestamp())
                      - Config.BLOCK_INTERVAL_SECONDS * 5)

        dapp_list_schema = DappListSchema(many=True)

        try:
            block_interval_first = db.session.query(func.min(BlockInterval.id)) \
                .filter(BlockInterval.time_start >= time_start).subquery()

            metric_latest_block_interval_id = (db.session.query(
                Metric.dapp_id, func.max(Metric.block_interval_id).label('metric_latest_block_interval'))
                                               .filter(Metric.block_interval_id >= block_interval_first)
                                               .group_by(Metric.dapp_id)
                                               .subquery())

            ranking_latest_block_interval_id = (
                db.session.query(Ranking.dapp_id,
                                 func.max(Ranking.block_interval_id).label('ranking_latest_block_interval'))
                    .filter(Ranking.block_interval_id >= block_interval_first)
                    .group_by(Ranking.dapp_id)
                    .subquery('ranking_latest_id'))

            ranking_latest = (db.session.query(Ranking.rank, RankingName.name.label('name'),
                                               Ranking.dapp_id, Ranking.block_interval_id)
                              .join(RankingName)
                              .filter(
                Ranking.block_interval_id == ranking_latest_block_interval_id.c.ranking_latest_block_interval)
                              .distinct()
                              .all())

            ranking_dict = {}
            if ranking_latest:
                for ranking in ranking_latest:
                    ranking_dapp_id = ranking.dapp_id
                    if ranking_dapp_id not in ranking_dict:
                        ranking_dict[ranking_dapp_id] = [ranking]
                    else:
                        ranking_dict[ranking_dapp_id].append(ranking)

                ranking_dict = {k: KeyedTuple([ranking_dict.get(k)], labels=['rankings']) for k in ranking_dict}

            # Get average ratings per dapp via subquery
            ratings = Review.query.with_entities(Review.dapp_id, func.avg(Review.rating).label('rating'),
                                                 func.count('*').label('rating_count')) \
                .group_by(Review.dapp_id).subquery()

            # Get list of all dapps
            results = Dapp.query \
                .join(Blockchain, Dapp.blockchain_id == Blockchain.id) \
                .join(Category, Dapp.category_id == Category.id) \
                .outerjoin(ratings, Dapp.id == ratings.c.dapp_id) \
                .outerjoin(metric_latest_block_interval_id, Dapp.id == metric_latest_block_interval_id.c.dapp_id) \
                .outerjoin(Metric, (Dapp.id == Metric.dapp_id) & (
                    Metric.block_interval_id == metric_latest_block_interval_id.c.metric_latest_block_interval)) \
                .filter(Dapp.name.ilike('%{}%'.format(name))) \
                .with_entities(Dapp.id, Dapp.name, Dapp.url, Dapp.uploaded_at, Dapp.tagline, Dapp.description,
                               Dapp.logo_path, Category.name.label('category'), Blockchain.symbol.label('blockchain'),
                               ratings.c.rating, ratings.c.rating_count, Metric.data.label('metrics')) \
                .all()

            if ranking_dict:
                for i, r in enumerate(results):
                    ranking_tuple = ranking_dict.get(r.id)
                    results[i] = KeyedTuple(r + ranking_tuple, r.keys() + ranking_tuple.keys())

            dapps = dapp_list_schema.dump(results).data

            return dapps, 200
        except Exception as e:
            print('EXCEPTION!!!: {}'.format(e))
            return [], 500


@api.route('/dapp_of_the_day')
class DappOfTheDay(Resource):
    """
    Get the dapp of the day
    """

    @staticmethod
    def get():
        try:
            dapp_of_the_day = DailyItem.get_by_id(2)
            dapp = GetDapp.get(dapp_of_the_day.item_id)

            return dapp[0], HTTPCodes.Success.value

        except Exception as e:
            print('EXCEPTION!!!: {}'.format(e))
            return {}, HTTPCodes.Success.value


@api.route('/featured')
class FeaturedDapp(Resource):
    """
    Get the featured dapps.
    """

    @staticmethod
    def get():
        try:
            category = request.args.get('category').upper()

            if category not in DappCategory.__members__:
                return {}, 404

            category = ' '.join([x.capitalize() for x in category.split('_')])

            # TODO: add date condition into filter
            results = (Featured.query.join(Category, Featured.page == Category.id)
                       .filter(Category.name == category).all())

            featured_schema = FeaturedSchema(many=True)
            featured_dapps = featured_schema.dump(results).data

            if not featured_dapps:
                return [], HTTPCodes.Success.value

            dapp_id_list = [dapp.get('dapp_id') for dapp in featured_dapps]
            dapp_list = ListDapps.get_selected_dapps(dapp_id_list)

            for i, dapp in enumerate(dapp_list):
                dapp_id = dapp.get('id')
                featured_dapp = next(filter(lambda x: x.get('dapp_id') == dapp_id, featured_dapps))
                dapp['banner_url'] = featured_dapp.get('banner_url')
                dapp['position'] = featured_dapp.get('position')
                dapp_list[i] = dapp

            return sorted(dapp_list, key=lambda x: x.get('position')), HTTPCodes.Success.value

        except Exception as e:
            return {'Error': 'Could not retrieve featured dapps.'}, 500
