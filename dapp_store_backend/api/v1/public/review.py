# -*- coding: utf-8 -*-
"""Public endpoints for Reviews."""
from flask import request
from flask_restplus import fields, Namespace, Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import joinedload

from dapp_store_backend.database import db
from dapp_store_backend.extensions import celery
from dapp_store_backend.settings import Config
from dapp_store_backend.models.daily_item import DailyItem
from dapp_store_backend.models.user import User
from dapp_store_backend.schemas.review_schema import ReviewSchema
from dapp_store_backend.schemas.review_of_the_day_schema import ReviewOfTheDaySchema
from dapp_store_backend.schemas.review_like_schema import ReviewLikeSchema
from . import Dapp
from . import Review
from . import ReviewLike

api = Namespace('review', description='Public review endpoints.', path='/public/review')


rate_review_put_fields = api.model('RateReivewPut', {
    'review_id': fields.Integer(required=True, description='ID of review.', example=1),
    'helpful': fields.Integer(description='Helpful (1) or not heplful (0).', example=1)
})

delete_rate_review_fields = api.model('DeleteRateReivew', {
    'review_id': fields.Integer(required=True, description='ID of review.', example=1)
})


@api.route('/add')
class PostReview(Resource):
    """
    Rate and review a dapp.
    """

    @jwt_required
    def post(self):
        current_user = get_jwt_identity()
        user = User.get_user_from_jwt_token(current_user)

        if not user:
            return {'Error': 'Invalid token'}, 400

        request_json = request.get_json()
        dapp_id = request_json.get('dapp_id')
        rating = request_json.get('rating')
        title = request_json.get('title')
        review = request_json.get('review')
        feature = request_json.get('feature')

        if not dapp_id or not rating or not title or not review:
            return {'Error': 'Required field is empty.'}, 400

        if feature and not all([1 if x in Config.RATING_TYPES else 0 for x in feature.keys()]):
            return {'Error': 'Invalid featured rating fields.'}, 400

        dapp = Dapp.get_by_id(dapp_id)

        try:
            celery.send_task('add_review_with_metrics', (user.address, dapp.address, user.id, request_json))
            return {'state': 1, 'message': 'Review submitted successfully.', 'result': ''}, 200
        except Exception as e:
            print('EXCEPTION!!!: {}'.format(e))
            return {'state': 0, 'message': 'Failed to submit review.', 'result': ''}, 500


@api.route('/vote')
class VoteReview(Resource):
    """
    Vote for a review as helpful/not helpful.
    """

    @api.expect(rate_review_put_fields)
    @jwt_required
    def put(self):
        current_user = get_jwt_identity()

        user = User.get_user_from_jwt_token(current_user)

        if not user:
            return {'Error': 'Invalid token'}, 404

        request_json = request.get_json()
        review_id = request_json.get('review_id')
        review = Review.get_by_id(review_id)

        if not review:
            return {'Error': 'Review not found.'}, 404

        # TODO: add review vote submission page
        try:
            review_like = ReviewLike(dapp_id=review.dapp_id,
                                     user_id=user.id,
                                     review_id=review_id,
                                     helpful=1)
            review_like.save()

            review_like_schema = ReviewLikeSchema()
            serialized = review_like_schema.dump(review_like).data

            return serialized, 200

        except Exception as e:
            print('ERROR!!!: {}'.format(e))
            return {'Error': 'Cannot like review twice.'}, 404


@api.route('/vote/delete')
class DeleteVoteReview(Resource):
    """
    Delete helpful vote for a review.
    """

    @api.expect(delete_rate_review_fields)
    @jwt_required
    def put(self):
        current_user = get_jwt_identity()

        user = User.get_user_from_jwt_token(current_user)

        if not user:
            return {'Error': 'Invalid token'}, 404

        request_json = request.get_json()
        review_id = request_json.get('review_id')
        review = Review.get_by_id(review_id)

        if not review:
            return {'Error': 'Review not found.'}, 404

        try:
            review_like = (ReviewLike.query.filter_by(dapp_id=review.dapp_id,
                                                      user_id=user.id,
                                                      review_id=review_id)
                           .first())
            review_like.delete()

            return {'message': 'Review vote removed successfully.'}, 200

        except Exception as e:
            print('ERROR!!!: {}'.format(e))
            return {'Error': 'Cannot delete review vote.'}, 400


@api.route('/<int:review_id>')
class UpdateReview(Resource):
    """
    Update existing review.
    """

    @staticmethod
    @jwt_required
    def put(review_id):
        current_user = get_jwt_identity()

        user = User.get_user_from_jwt_token(current_user)

        if not user:
            return {'Error': 'Invalid token'}, 404

        request_json = request.get_json()
        rating = request_json.get('rating')
        review_text = request_json.get('review')
        feature = request_json.get('feature')
        title = request_json.get('title')

        review = Review.get_by_id(review_id)

        if not review:
            return {'Error': 'Review does not exist.'}, 404

        if rating:
            review.rating = rating

        if review_text:
            review.review = review_text

        if feature:
            review.feature = feature

        if title:
            review.title = title

        db.session.commit()

        review_schema = ReviewSchema()
        serialized = review_schema.dump(review).data

        return serialized, 200


@api.route('/<int:review_id>')
class DeleteReview(Resource):
    """
    Delete existing review.
    """

    @staticmethod
    @jwt_required
    def delete(review_id):
        current_user = get_jwt_identity()

        user = User.get_user_from_jwt_token(current_user)

        if not user:
            return {'Error': 'Invalid token'}, 404

        review = Review.get_by_id(review_id)

        if not review:
            return {'Error': 'Review does not exist.'}, 404

        if user.id != review.user_id:
            return {'Error': 'You do not own this review.'}, 401

        ReviewLike.query.filter_by(review_id=review_id).delete()
        Review.query.filter_by(id=review_id).delete()
        db.session.commit()

        return True, 200


@api.route('/review_of_the_day')
class ReivewOfTheDay(Resource):
    """
    Get review of the day.
    """
    def get(self):

        try:
            review_id = DailyItem.get_by_id(1)

            review_of_the_day = (Review.query.join(Dapp)
                                 .options(joinedload(Review.dapp))
                                 .filter(Review.id == review_id.item_id)
                                 .first())

            review_schema = ReviewOfTheDaySchema(exclude=['dapp'])
            serialized = review_schema.dump(review_of_the_day).data

            return serialized, 200

        except Exception as e:
            print('ERROR!!!: {}'.format(e))
            return {}, 200
