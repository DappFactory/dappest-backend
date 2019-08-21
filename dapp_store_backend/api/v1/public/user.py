# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from datetime import timedelta
from flask import current_app, request
from flask_restplus import Namespace, Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from boto3 import client
from sqlalchemy.orm import joinedload

from dapp_store_backend.database import db
from dapp_store_backend.models.dapp import Dapp
from dapp_store_backend.models.review import Review
from dapp_store_backend.models.blockchain import Blockchain
from dapp_store_backend.utilities import verify_eth_address, verify_eth_signed_message
from dapp_store_backend.schemas.user_schema import UserSchema
from dapp_store_backend.schemas.user_profile_schema import UserProfileSchema
from dapp_store_backend.utilities import generate_nonce, valdate_image_type, upload_image_to_s3
from . import User

api = Namespace('user', description='Public user endpoints.', path='/public/user')


@api.route('/login', strict_slashes=False)
class GetUserAndNonce(Resource):
    """
    Gets the user associated with the address.
    """

    @staticmethod
    def post():
        public_address = request.get_json().get('public_address')

        if not public_address or not verify_eth_address(public_address):
            return {'Error': 'Invalid ETH address.'}, 404

        result = User.query.filter_by(address=public_address).first()

        if result is None:
            try:
                user = User(address=public_address,
                            username=public_address,
                            blockchain_id=1)
                user.save()

                return {'username': public_address,
                        'nonce': user.nonce}, 200
            except Exception as e:
                print('EXCEPTION!!!!!: {}'.format(e))
                return {'Error': 'Error creating user with public address: {}'.format(public_address)}, 404

        user_schema = UserSchema()
        user = user_schema.dump(result).data

        return {'username': user.get('username'),
                'nonce': user.get('nonce')}, 200


@api.route('/authorize')
class AuthorizeUser(Resource):
    """
    Authorize the user and return JWT token and user.
    """

    @staticmethod
    def post():
        request_json = request.get_json()

        public_address = request_json.get('public_address')
        signature = request_json.get('signature')

        user = User.query.filter(User.address == public_address).first()

        if not user:
            return {'Error': 'Public address not associated with a user.'}, 500

        message = 'Logging in as: {username}, nonce: {nonce}'.format(username=user.username, nonce=user.nonce)

        if not verify_eth_signed_message(public_address, message, signature):
            User.query.filter(User.address == public_address).delete()
            db.session.commit()
            return {'Error': 'Failed to validate public address.'}, 500

        token = create_access_token({'id': user.id,
                                     'address': user.address}, expires_delta=timedelta(days=1))

        user.nonce = generate_nonce()
        db.session.commit()

        user_schema = UserSchema()
        serialized_user = user_schema.dump(user).data
        serialized_user['token'] = token

        return serialized_user, 200


@api.route('/update')
class UpdateUser(Resource):
    """
    Update user information.
    """

    @jwt_required
    def post(self):
        current_user = get_jwt_identity()
        user = User.get_user_from_jwt_token(current_user)

        if not user:
            return {'Error': 'Invalid token'}, 404

        request_json = request.get_json()
        username = request_json.get('username')
        email = request_json.get('email')
        profile_picture = request_json.get('profile_picture')

        if username and username != user.username:
            check_username = User.query.filter(User.username == username).first()

            if check_username:
                return {'Error': 'Username already taken.'}, 404

            user.username = username

        if email and email != user.email:
            check_email = User.query.filter(User.email == email).first()

            if check_email:
                return {'Error': 'Email already taken.'}, 404

            user.email = email

        if profile_picture:
            profile_picture_base64_string = profile_picture.get('image')
            profile_picture_file_type = profile_picture.get('file_type')

            # Validate logo
            logo_error = valdate_image_type(profile_picture_base64_string, profile_picture_file_type)
            if logo_error:
                return {'Logo Error': logo_error}, 404

            s3_client = client('s3',
                               aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                               aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'])
            bucket = current_app.config['S3_BUCKET_NAME']

            # Upload image to S3
            try:
                profile_picture_path = upload_image_to_s3(s3_client, bucket, profile_picture_base64_string,
                                                          profile_picture_file_type,
                                                          path=f'user/{user.s3_id}/profile_picture')
            except Exception as e:
                print(e)
                return {'Error': 'Failed to upload image to S3.'}, 500

            user.profile_picture = profile_picture_path

        db.session.commit()

        user_schema = UserSchema(exclude=['profile_picture'])
        user = user_schema.dump(user).data

        return user, 200


@api.route('/profile/<string:address>')
class UserProfile(Resource):
    """
    Get user profile.
    """

    @staticmethod
    def get(address):

        user = User.query \
                .outerjoin(Review).options(joinedload(User.reviews)) \
                .join(Blockchain).options(joinedload(User.blockchain)) \
                .join(Dapp).options(joinedload(User.dapps).noload(Dapp.reviews)) \
                .filter((User.address == address)).first()

        if not user:
            return {'Error': 'User not found.'}, 404

        user_schema = UserProfileSchema(exclude=['review_likes', 'profile_picture', 'nonce'])
        serialized_user = user_schema.dump(user).data

        return serialized_user, 200

