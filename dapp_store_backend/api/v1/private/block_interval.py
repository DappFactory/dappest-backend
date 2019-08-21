# -*- coding: utf-8 -*-
"""Private block interval endpoints."""
from flask import request
from flask_restplus import fields, Namespace, Resource
from sqlalchemy import exc
from sqlalchemy.orm import noload

from dapp_store_backend.enums.status import HTTPCodes

from dapp_store_backend.database import db
from dapp_store_backend.models.block_interval import BlockInterval
from dapp_store_backend.schemas.block_interval_schema import BlockIntervalSchema

api = Namespace('block_interval', description='Private block interval endpoints.', path='/private/block_interval')

# Block api.models
block_interval_get_fields = api.model('BlockIntervalGet', {
    'id': fields.Integer(required=True, description='ID of block interval.', example=1),
    'blockchain_id': fields.Integer(required=True, description='ID of blockchain.', example=1),
    'time_start': fields.Integer(required=True, description='Start time (inclusive) of block interval in UTC (seconds).', example=86400),
    'time_stop': fields.Integer(required=True, description='Stop time (exclusive) of block interval in UTC (seconds).', example=186400),
    'block_start': fields.Integer(required=True, description='Start block (inclusive) of block interval.', example=1000),
    'block_stop': fields.Integer(required=True, description='Stop block (exclusive) of block interval.', example=1500),
})

block_interval_post_fields = api.model('BlockIntervalPost', {
    'blockchain_id': fields.Integer(required=True, description='ID of blockchain.', example=1),
    'time_start': fields.Integer(required=True, description='Start time (inclusive) of block interval in UTC (seconds).', example=86400),
    'time_stop': fields.Integer(required=True, description='Stop time (exclusive) of block interval in UTC (seconds).', example=186400),
    'block_start': fields.Integer(description='Start block (inclusive) of block interval.', example=1000),
    'block_stop': fields.Integer(description='Stop block (exclusive) of block interval.', example=1500)
})

block_interval_put_fields = api.model('BlockIntervalPut', {
    'id': fields.Integer(required=True, description='ID of block.', example=1),
    'block_start': fields.Integer(description='Start block (inclusive) of block interval.', example=1000),
    'block_stop': fields.Integer(description='Stop block (exclusive) of block interval.', example=1500)
})

# Blockchain api.models
blockchain_post_fields = api.model('BlockchainPost', {
    'name': fields.String(required=True, description='Name of blockchain.', example='Ethereum'),
    'symbol': fields.String(required=True, description='Symbol of blockchain.', example='ETH'),
})

blockchain_get_fields = api.model('BlockchainGet', {
    'name': fields.String(required=True, description='Name of blockchain.', example='Ethereum'),
    'symbol': fields.String(required=True, description='Symbol of blockchain.', example='ETH'),
    'id': fields.Integer(description='ID of blockchain in database.')
})

blockchain_get_list_fields = api.model('BlockchainGetList', {
    'blockchains': fields.List(fields.Nested(blockchain_get_fields))
})

# Category models
category_fields = api.model('Category', {
    'name': fields.String(required=True, description='Name of category.', example='Game')
})

# Dapp models
dapp_get_fields = api.model('DappGet', {
    'id': fields.Integer(required=True, description='ID of dapp.', example=1),
    'symbol': fields.String(required=True, description='Symbol of blockchain platform supporting the dapp.', example='ETH'),
    'address': fields.List(fields.String, required=True, description='List of dapp contract addresses.', example=['0xa1', '0xb2'])
})

dapp_get_list_fields = api.model('DappGetList', {
    'dapps': fields.List(fields.Nested(dapp_get_fields))
})

# Dapp transaction models
dapp_transactions_fields = api.model('DappTransactions', {
    'addresses': fields.List(fields.String, description='List of addresses.'),
    'start_block': fields.Integer(required=True, description='Start block.', example='0'),
    'end_block': fields.Integer(required=True, description='End block.', example='9999999')
})

# Metric models
metric_fields = api.model('Metric', {
    'dapp_id': fields.Integer(required=True, description='ID for dapp.', example=1),
    'users': fields.Integer(required=True, description='Unique users for a dapp.', example=99),
    'volume': fields.Integer(required=True, description='Total volume for a dapp.', example=100000),
    'transactions': fields.Integer(required=True, description='Total number of transactions for a dapp.', example=384)
})

metric_list_fields = api.model('MetricList', {
    'metrics': fields.List(fields.Nested(metric_fields))
})

# Submission models
approve_submission_fields = api.model('Approve_submission', {
    'id': fields.Integer(required=True, description='ID of review/dapp.', example='10'),
    'approval': fields.Integer(required=True, description='Approve or deny.', example='1')
})


@api.route('/add')
class AddBlockInterval(Resource):
    """
    Add block interval to database.
    """
    @api.expect(block_interval_post_fields)
    @api.marshal_with(block_interval_get_fields)
    def post(self):
        request_json = request.get_json()

        # get the timing fields of the block interval
        time_start = request_json.get('time_start')
        time_stop = request_json.get('time_stop')
        block_start = request_json.get('block_start')
        block_stop = request_json.get('block_stop')

        # perform timing checks on the block intervals
        if block_start and block_stop:
            assert (block_stop > block_start), 'Stop block must be greater than start block.'
            assert (time_stop > time_start), 'Stop time of this block must be greater then the start time.'

        try:
            block_interval = BlockInterval(blockchain_id=request_json.get('blockchain_id'),
                                           time_start=time_start,
                                           time_stop=time_stop,
                                           block_start=block_start,
                                           block_stop=block_stop)
            block_interval.save()

            block_interval_schema = BlockIntervalSchema()
            return block_interval_schema.dump(block_interval).data, HTTPCodes.Success.value
        except exc.IntegrityError as e:
            db.session().rollback()
            return {'Error': '({}, {}) already exists.'.format(request_json.get('blockchain_id'),
                                                               request_json.get('timestamp'))}, HTTPCodes.Not_Found.value


@api.route('/get/<int:blockchain_id>/<int:epoch_time>')
class GetBlockInterval(Resource):
    """
    Get block interval from database.
    """
    @api.marshal_with(block_interval_get_fields, skip_none=True)
    def get(self, blockchain_id, epoch_time):
        block_interval_schema = BlockIntervalSchema()
        results = BlockInterval.query.options(noload('*')) \
            .filter_by(blockchain_id=blockchain_id,
                       time_start=epoch_time).first()

        return block_interval_schema.dump(results).data, HTTPCodes.Success.value


@api.route('/update')
class UpdateBlockInterval(Resource):
    """
    Get block interval from database.
    """
    @api.expect(block_interval_put_fields)
    @api.marshal_with(block_interval_get_fields, skip_none=True)
    def put(self):
        request_json = request.get_json()
        start = request_json.get('block_start')
        stop = request_json.get('block_stop')

        block_interval = BlockInterval.query.options(noload('*')).get(request_json.get('id'))

        if not block_interval or (not start and not stop):
            return {}, HTTPCodes.Success.value

        if not block_interval.block_start:
            block_interval.block_start = start

        if not block_interval.block_stop:
            assert (
                stop > block_interval.block_start), 'Stop block must be greater than start block.'
            block_interval.block_stop = stop

        db.session.commit()

        block_interval_schema = BlockIntervalSchema()

        return block_interval_schema.dump(block_interval).data, HTTPCodes.Success.value