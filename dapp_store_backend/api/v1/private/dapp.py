# -*- coding: utf-8 -*-
"""Private dapp endpoints."""
from flask import request
from flask_restplus import fields
from flask_restplus import Namespace, Resource
from sqlalchemy import exc

from dapp_store_backend.database import db
from dapp_store_backend.enums.status import HTTPCodes
from dapp_store_backend.models.dapp import Dapp
from dapp_store_backend.models.blockchain import Blockchain
from dapp_store_backend.models.featured import Featured
from dapp_store_backend.schemas.dapp_list_address_schema import DappListAddressSchema


api = Namespace('dapp', description='Private dapp endpoints.', path='/private/dapp')

dapp_get_fields = api.model('DappGet', {
    'id': fields.Integer(required=True, description='ID of dapp.', example=1),
    'symbol': fields.String(required=True, description='Symbol of blockchain platform supporting the dapp.', example='ETH'),
    'address': fields.List(fields.String, required=True, description='List of dapp contract addresses.', example=['0xa1', '0xb2'])
})

dapp_get_list_fields = api.model('DappGetList', {
    'dapps': fields.List(fields.Nested(dapp_get_fields))
})


@api.route('/list')
class ListDapps(Resource):
    """
    Get list of dapps with only blockchain symbol and address.
    """
    @api.marshal_with(dapp_get_list_fields)
    def get(self):
        dapp_list_address_schema = DappListAddressSchema(many=True)
        results = Dapp.query.join(Blockchain).with_entities(Dapp.id, Blockchain.symbol,
                                                            Dapp.address).all()
        dapps = dapp_list_address_schema.dump(results).data

        return {'dapps': dapps}, HTTPCodes.Success.value


@api.route('/featured')
class AddFeaturedDapp(Resource):
    """
    Add featured dapp.
    """
    def post(self):
        request_json = request.get_json()

        try:
            # TODO: mannually add banner into dapp/{UUID}/banner folder
            featured_dapp = Featured(page=request_json.get('page'),
                                     position=request_json.get('position'),
                                     dapp_id=request_json.get('dapp_id'),
                                     banner_path=request_json.get('banner_path'),
                                     duration=request_json.get('duration'),
                                     start_date=request_json.get('start_date'),
                                     end_date=request_json.get('end_date'))
            featured_dapp.save()
        except exc.IntegrityError as e:
            db.session().rollback()
            return {'Error': 'Featured dapp already exists'}, 404

        return request_json, HTTPCodes.Success.value