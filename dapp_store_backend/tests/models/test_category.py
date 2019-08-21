# -*- coding: utf-8 -*-
import pytest

from dapp_store_backend.models.category import Category


@pytest.mark.usefixtures('session')
class TestCategory:
    """
    Tests for the category model.
    """

    def test_get_by_id(self, session):
        category = Category(id=2,
                            name='Social')
        category.save()

        retrieved = Category.get_by_id(category.id)
        assert retrieved == category
