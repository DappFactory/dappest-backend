# -*- coding: utf-8 -*-
import pytest

from dapp_store_backend.models.mailing_list import MailingList


@pytest.mark.usefixtures('session')
class TestMailingList:
    """
    Tests for the mailing list model.
    """

    def test_get_by_id(self, session):
        mailing_list = MailingList(id=1,
                                   email='testemail@gmail.com')

        mailing_list.save()

        retrieved = MailingList.get_by_id(mailing_list.id)
        assert retrieved == mailing_list
