#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask_script import Manager, Shell, Server
from flask_script.commands import Clean, ShowUrls
from flask_migrate import MigrateCommand

from dapp_store_backend.app import create_app
from dapp_store_backend.settings import DevConfig, ProdConfig
from dapp_store_backend.database import db

print('##############################')
print('CALL TO manage.py')

if os.environ.get("DAPP_STORE_BACKEND_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

manager = Manager(app)


def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db}


@manager.command
def test():
    """Runs the tests."""
    import pytest
    pytest.main(["-s", "dapp_store_backend/tests"])


@manager.command
def init_data():

    from psycopg2 import connect, sql

    # CSV files to insert into table
    data_table = [('ranking_name.csv', 'ranking_name'),
                  ('blockchain.csv', 'blockchain'),
                  ('daily_item.csv', 'daily_item'),
                  ('category.csv', 'category'),
                  ('user.csv', 'dappest_user'),
                  ('dapp.csv', 'dapp'),
                  ('featured.csv', 'featured'),
                  ('review.csv', 'review')]
    dir = os.path.dirname(os.path.realpath(__file__))

    # db connection
    conn = connect(
        'host={host} dbname={dbname} user={user} password={password}'.format(
            host=os.environ.get('POSTGRES_HOST'),
            dbname=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD')
        ))
    cur = conn.cursor()

    for (file, table) in data_table:

        # Get number of rows in each table
        cur.execute('SELECT count(*) from {}'.format(table))
        result = cur.fetchone()

        if result[0] == 0 and table != 'user':

            print('Initializing data for {} ...'.format(table))

            path = os.path.join(dir, 'test_data', file)

            with open(path, 'r') as f:
                next(f)

                # Insert data from .csv into db
                # TODO: change dapp address to JSON when uploading
                cur.copy_from(f, table, sep=',')

                # Update sequence tables
                cur.execute(
                    sql.SQL("SELECT setval('{}', max(id)) FROM {};").format(
                        sql.Identifier('{}_id_seq'.format(table)), sql.Identifier(table)))
                conn.commit()

    conn.close()


# link cli keywords to flask commands
manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)
manager.add_command("urls", ShowUrls())
manager.add_command("clean", Clean())

if __name__ == '__main__':

    manager.run()
