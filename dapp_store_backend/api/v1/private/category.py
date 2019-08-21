# -*- coding: utf-8 -*-
"""Private category endpoints."""
from flask import request
from flask_restplus import fields, Namespace, Resource
from sqlalchemy import exc

from dapp_store_backend.database import db
from dapp_store_backend.models.category import Category


api = Namespace('category', description='Private category endpoints.', path='/private/category')

category_fields = api.model('Category', {
    'name': fields.String(required=True, description='Name of category.', example='Game')
})


@api.route('/add')
class AddCategory(Resource):
    """
    Add category to database.
    """
    @api.expect(category_fields)
    def post(self):

        request_json = request.get_json()

        try:
            category = Category(name=request_json.get('name'))
            category.save()
        except exc.IntegrityError as e:
            db.session().rollback()
            return {'Error': '{} already exists.'.format(request_json.get('name'))}, 404

        return request_json, 200
