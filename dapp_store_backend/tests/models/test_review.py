# -*- coding: utf-8 -*-
import pytest

from dapp_store_backend.models.review import Review


@pytest.mark.usefixtures('session')
class TestReview:
    """
    Tests for the review model.
    """

    def test_get_by_id(self, session):
        review = Review(dapp_id=1,
                        user_id=1,
                        rating=2,
                        title='Review title',
                        review='Test review.')

        review.save()

        retrieved = Review.get_by_id(review.id)
        assert retrieved == review
