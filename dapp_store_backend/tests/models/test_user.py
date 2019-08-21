# -*- coding: utf-8 -*-
import datetime as dt
import pytest

from dapp_store_backend.models.user import User


@pytest.mark.usefixtures('session')
class TestUser:
    """
    Tests for the user model.
    """

    def test_create_user_on_metamask_login(self, session):
        user = User(id=2,
                    address='0xC257274276a4E539741Ca11b590B9447B26A8051',
                    username='0xC257274276a4E539741Ca11b590B9447B26A8051',
                    blockchain_id=1)

        user.save()

        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    def test_uploaded_at_defaults_to_datetime(self, session):
        user = User(id=2,
                    address='0xC257274276a4E539741Ca11b590B9447B26A8051',
                    username='0xC257274276a4E539741Ca11b590B9447B26A8051',
                    blockchain_id=1)

        user.save()

        assert bool(user.created_at)
        assert isinstance(user.created_at, dt.datetime)
