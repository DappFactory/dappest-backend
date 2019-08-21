# -*- coding: utf-8 -*-
"""Private blockchain endpoints."""
from flask import request
from flask_restplus import fields, Namespace, Resource
from sqlalchemy import exc

from dapp_store_backend.extensions import celery
from dapp_store_backend.database import db
from dapp_store_backend.models.blockchain import Blockchain
from dapp_store_backend.schemas.blockchain_schema import BlockchainSchema

api = Namespace('blockchain', description='Private blockchain endpoints.', path='/private/blockchain')

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


@api.route('/add')
class AddBlockchain(Resource):
    """
    Add blockchain to database.
    """
    @api.expect(blockchain_post_fields)
    def post(self):
        request_json = request.get_json()
        try:
            blockchain = Blockchain(name=request_json.get('name'),
                                    symbol=request_json.get('symbol'))
            blockchain.save()
        except exc.IntegrityError as e:
            db.session().rollback()
            return {'Error': '({}, {}) already exists.'.format(request_json.get('name'),
                                                               request_json.get('symbol'))}, 404

        return request_json, 200


@api.route('/list')
class ListBlockchains(Resource):
    """
    Get list of blockchains.
    """
    @api.marshal_with(blockchain_get_list_fields)
    def get(self):
        blockchain_schema = BlockchainSchema(many=True)
        results = Blockchain.query.all()
        blockchains = blockchain_schema.dump(results).data

        return {'blockchains': blockchains}, 200


@api.route('/add/task')
class AddBlockchainTask(Resource):
    """
    Add blockchain to database.
    """
    @api.expect(blockchain_post_fields)
    def post(self):
        request_json = request.get_json()

        celery.send_task('add_blockchain_task', args=[request_json.get('name'), request_json.get('symbol')])

        return request_json, 200
