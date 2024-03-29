"""empty message

Revision ID: 052fcb9502e9
Revises: 3b0581b83379
Create Date: 2018-09-18 21:40:47.392598

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '052fcb9502e9'
down_revision = '3b0581b83379'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'block_interval', ['id'])
    op.create_unique_constraint(None, 'blockchain', ['id'])
    op.create_unique_constraint(None, 'category', ['id'])
    op.create_unique_constraint(None, 'daily_item', ['id'])
    op.create_unique_constraint(None, 'dapp', ['id'])
    op.create_unique_constraint(None, 'dapp_submission', ['id'])
    op.create_unique_constraint(None, 'dappest_user', ['id'])
    op.create_unique_constraint(None, 'mailing_list', ['id'])
    op.create_unique_constraint(None, 'metric', ['id'])
    op.create_unique_constraint(None, 'ranking', ['id'])
    op.create_unique_constraint(None, 'ranking_name', ['id'])
    op.create_unique_constraint(None, 'review', ['id'])
    op.create_unique_constraint(None, 'review_like', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'review_like', type_='unique')
    op.drop_constraint(None, 'review', type_='unique')
    op.drop_constraint(None, 'ranking_name', type_='unique')
    op.drop_constraint(None, 'ranking', type_='unique')
    op.drop_constraint(None, 'metric', type_='unique')
    op.drop_constraint(None, 'mailing_list', type_='unique')
    op.drop_constraint(None, 'dappest_user', type_='unique')
    op.drop_constraint(None, 'dapp_submission', type_='unique')
    op.drop_constraint(None, 'dapp', type_='unique')
    op.drop_constraint(None, 'daily_item', type_='unique')
    op.drop_constraint(None, 'category', type_='unique')
    op.drop_constraint(None, 'blockchain', type_='unique')
    op.drop_constraint(None, 'block_interval', type_='unique')
    # ### end Alembic commands ###
