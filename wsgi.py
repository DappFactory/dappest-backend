#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dapp_store_backend.app import create_app
from dapp_store_backend.settings import ProdConfig

print('##############################')
print('CALL TO wsgi.py')

app = create_app(ProdConfig)

if __name__ == '__main__':

    app.run()
