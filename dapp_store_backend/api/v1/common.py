# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import request
from flask_restplus import fields, Namespace, Resource

from dapp_store_backend.enums.status import HTTPCodes
from dapp_store_backend.models.contact_form import ContactForm
from dapp_store_backend.models.mailing_list import MailingList


api = Namespace('public', description='Public endpoints.', path='/public')


# define the contact fields that api must get for contact
contact_fields = api.model('Contact', {
    'name': fields.String(required=True, description='Name of person.', example='John Doe'),
    'email': fields.String(required=True, description='Email of person.', example='johndoe@gmail.com'),
    'message': fields.String(required=True)
})


@api.route('/featured/<string:page>')
class Featured(Resource):

    def get(self, page):
        return None


@api.route('/subscribe')
class Subscribe(Resource):
    """
    Add email to mailing list.
    """

    def post(self):
        request_json = request.get_json()

        try:
            entry = MailingList(email=request_json.get('email'))
            entry.save()
            return {'message': 'Successfully added email to mailing list'}, 200

        except:
            return {'Error': 'Failed to add email to mailing list.'}, 404


@api.route('/contact')
class ContactFormSubmit(Resource):
    """
    Submit contact form.
    """

    @api.expect(contact_fields)
    def post(self):
        request_json = request.get_json()

        contactform = ContactForm(name=request_json.get('name'),
                                  email=request_json.get('email'),
                                  message=request_json.get('message'))
        contactform.save()

        return request_json, HTTPCodes.Success.value
