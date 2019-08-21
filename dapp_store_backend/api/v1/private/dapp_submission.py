# -*- coding: utf-8 -*-
"""Private dapp submission endpoints."""
from flask import current_app, request
from flask_restplus import fields, Namespace, Resource
from boto3 import client

from dapp_store_backend.database import db
from dapp_store_backend.extensions import celery
from dapp_store_backend.models.dapp import Dapp
from dapp_store_backend.enums.status import DappSubmissionStatus
from dapp_store_backend.models.dapp_submission import DappSubmission
from dapp_store_backend.schemas.dapp_submission_schema import DappSubmissionSchema
from dapp_store_backend.utilities import move_recursive_s3, move_s3


api = Namespace('dapp_submission', description='Private dapp submission endpoints.', path='/private/dapp_submission')

approve_submission_fields = api.model('Approve_submission', {
    'id': fields.Integer(required=True, description='ID of dapp submission.', example='10'),
    'approval': fields.Integer(required=True, description='Approve or deny.', example='1')
})


@api.route('/view')
class ViewDappSubmission(Resource):
    """
    View all dapp submissions.
    """

    def get(self):
        # TODO: check if can make primary keys of two tables linked
        dapp_submissions_schema = DappSubmissionSchema(many=True)

        results = DappSubmission.query.filter(DappSubmission.status == DappSubmissionStatus.SUBMITTED.value).all()
        dapp_submissions = dapp_submissions_schema.dump(results).data

        return dapp_submissions, 200


@api.route('/approve')
class ApproveDappSubmission(Resource):
    """
    Approve/deny dapp submissions.
    """
    @api.expect(approve_submission_fields)
    def post(self):
        request_json = request.get_json()
        dapp_submission_id = request_json.get('id')
        approval = request_json.get('approval')

        assert (approval == DappSubmissionStatus.APPROVED.value or
                approval == DappSubmissionStatus.DENIED.value), 'Approval value not allowed: {}'.format(approval)
        assert isinstance(dapp_submission_id, int), 'Id value required.'

        submission = DappSubmission.query.get(dapp_submission_id)

        if submission and submission.status == DappSubmissionStatus.SUBMITTED.value:
            if approval:
                submission.status = DappSubmissionStatus.APPROVED.value

                # Move files to different folder in S3
                s3_client = client('s3',
                                   aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                                   aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'])
                bucket = current_app.config['S3_BUCKET_NAME']

                try:
                    dapp_logo_path = move_s3(s3_client, bucket, submission.logo_path,
                                             submission.logo_path.replace('dapp_submission', 'dapp'))

                    submission_screenshot_path = 'dapp_submission/{uuid}/screenshots'.format(uuid=submission.s3_id)
                    dapp_screenshots_path = move_recursive_s3(s3_client, bucket, submission_screenshot_path,
                                                              submission_screenshot_path.replace('dapp_submission', 'dapp'))
                except Exception as e:
                    print(e)
                    return {'Error': 'Could not upload images to S3.'}, 404

                dapp = Dapp(name=submission.name,
                            url=submission.url,
                            address=submission.address,
                            author=submission.author,
                            email=submission.email,
                            logo_path=dapp_logo_path,
                            screenshot=dapp_screenshots_path,
                            tagline=submission.tagline,
                            description=submission.description,
                            whitepaper=submission.whitepaper,
                            social_media=submission.social_media,
                            blockchain_id=submission.blockchain_id,
                            category_id=submission.category_id,
                            user_id=submission.user_id,
                            s3_id=submission.s3_id,
                            launch_date=submission.launch_date)
                dapp.save()
            else:
                submission.status = DappSubmissionStatus.DENIED.value
                db.session.commit()

            return request_json, 200

        return {'Error': 'Failed to approve/deny dapp submission.'}, 404


@api.route('/update')
class UpdateDappSubmission(Resource):
    """
    Update dapp submission.
    """

    def post(self):
        request_json = request.get_json()

        dapp_submission_id = request_json.get('id')
        dapp_submission = DappSubmission.query.get(dapp_submission_id)

        celery.send_task('update_contract_deployment_date', (dapp_submission.id, dapp_submission.address))

        return {'status': 'SUCCESS'}, 200
