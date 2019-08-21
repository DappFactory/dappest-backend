# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest

from dapp_store_backend.models.dapp import Dapp
from dapp_store_backend.models.block_interval import BlockInterval
from dapp_store_backend.models.blockchain import Blockchain


@pytest.mark.usefixtures('session')
class TestDapp:
    """
    Test for the dapps model:

    - name
    - owner
    - uploaded_at

    """

    def test_get_by_id(self, session):
        dapp = Dapp(id=2,
                    name='CryptoPandas',
                    url='cryptopandas.co',
                    address=['0x048717ea892f23fb0126f00640e2b18072efd9d2'],
                    author=['Modelo Brown'],
                    email='cryptopandas@gmail.com',
                    logo_path='tmp111.png',
                    screenshot=['tmp1111.png', 'tmp112.png'],
                    tagline='tagline',
                    description='Long descrption here.',
                    category_id=1,
                    blockchain_id=1,
                    user_id=1,
                    s3_id='0f0bedea-9922-490c-bac9-fe06fdfa55a4')

        session.add(dapp)
        session.commit()

        retrieved = Dapp.get_by_id(dapp.id)
        assert retrieved == dapp

    def test_add_list(self, session):
        dapp = Dapp(id=2,
                    name='CryptoPandas',
                    url='cryptopandas.co',
                    address=['0x048717ea892f23fb0126f00640e2b18072efd9d2',
                             '0xC257274276a4E539741Ca11b590B9447B26A8051'],
                    author=['Right Left'],
                    email='cryptopandas@gmail.com',
                    logo_path='tdjfgnd.jpeg',
                    screenshot=['dgd.png', 'dgjg.tiff'],
                    tagline='tagline',
                    description='Long descrption here.',
                    category_id=1,
                    blockchain_id=1,
                    user_id=1,
                    s3_id='1f0bedea-9922-490c-bac8-fe06fdfa55a4')

        session.add(dapp)
        session.commit()

        retrieved = Dapp.get_by_id(dapp.id)
        assert retrieved == dapp

    def test_uploaded_at_defaults_to_datetime(self, session):
        dapp = Dapp(id=2,
                    name='CryptoPandas',
                    url='cryptopandas.co',
                    address=['0x048717ea892f23fb0126f00640e2b18072efd9d2'],
                    author=['Tag Bob'],
                    email='cryptopandas@gmail.com',
                    logo_path='dkfng.tiff',
                    screenshot=['sfda.png'],
                    tagline='tagline',
                    description='Long descrption here.',
                    category_id=1,
                    blockchain_id=1,
                    user_id=1,
                    s3_id='0f0badea-9922-490c-bac8-fe06fdfa55a4')

        session.add(dapp)
        session.commit()

        assert bool(dapp.uploaded_at)
        assert isinstance(dapp.uploaded_at, dt.datetime)
