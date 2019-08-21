# -*- coding: utf-8 -*-
"""Private metric endpoints."""
from flask import request
from flask_restplus import fields, Namespace, Resource
from sqlalchemy import exc

from dapp_store_backend.database import db
from dapp_store_backend.models.metric import Metric


api = Namespace('metric', description='Private metric endpoints.',
                path='/private/metric')

metric_fields = api.model('Metric', {
    'dapp_id': fields.Integer(required=True, description='ID for dapp.', example=1),
    'users': fields.Integer(required=True, description='Unique users for a dapp.', example=99),
    'volume': fields.Integer(required=True, description='Total volume for a dapp.', example=100000),
    'transactions': fields.Integer(required=True, description='Total number of transactions for a dapp.', example=384)
})

metric_list_fields = api.model('MetricList', {
    'metrics': fields.List(fields.Nested(metric_fields))
})


@api.route('/add')
class AddMetric(Resource):
    """
    Add user/volume/transactions metrics for a dapp.
    """
    @api.expect(metric_list_fields)
    def post(self):
        metrics = request.get_json().get('metrics')

        if metrics:
            for dapp_metrics in metrics:
                metric = Metric(dapp_id=dapp_metrics.get('dapp_id'),
                                block_interval_id=dapp_metrics.get(
                                    'block_interval_id'),
                                data=dapp_metrics.get('metrics'))

                db.session.add(metric)

            try:
                db.session.commit()
            except exc.IntegrityError as e:
                db.session().rollback()
                print(
                    'Metric already exists for specified block_interval, rolling back batch of metrics.')
                return {'status': 'FAILED'}, 404

        return {'status': 'SUCCESS'}, 200
