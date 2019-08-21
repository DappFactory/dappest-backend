"""empty message

Revision ID: 3b0581b83379
Revises: 
Create Date: 2018-09-18 08:44:57.132653

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3b0581b83379'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mailing_list',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('id')
    )
    op.create_table('daily_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_name', sa.String(length=32), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('item_name')
    )
    op.create_table('blockchain',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('symbol', sa.String(length=16), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('symbol')
    )
    op.create_table('ranking_name',
    sa.Column('id', sa.SmallInteger(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('block_interval',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('blockchain_id', sa.Integer(), nullable=False),
    sa.Column('time_start', sa.Integer(), nullable=False),
    sa.Column('time_stop', sa.Integer(), nullable=False),
    sa.Column('block_start', sa.Integer(), nullable=False),
    sa.Column('block_stop', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['blockchain_id'], ['blockchain.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('dappest_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=64), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('profile_picture', sa.String(length=100), nullable=True),
    sa.Column('blockchain_id', sa.Integer(), nullable=False),
    sa.Column('s3_id', postgresql.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('nonce', sa.String(length=9), nullable=False),
    sa.ForeignKeyConstraint(['blockchain_id'], ['blockchain.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('s3_id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('dapp',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('url', sa.String(length=80), nullable=False),
    sa.Column('address', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('author', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('logo_path', sa.String(length=100), nullable=False),
    sa.Column('screenshot', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('tagline', sa.String(length=40), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=False),
    sa.Column('whitepaper', sa.String(length=80), nullable=True),
    sa.Column('social_media', postgresql.JSONB(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('blockchain_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('s3_id', postgresql.UUID(), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(), nullable=False),
    sa.Column('launch_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['blockchain_id'], ['blockchain.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['dappest_user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('logo_path'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('s3_id'),
    sa.UniqueConstraint('screenshot'),
    sa.UniqueConstraint('url')
    )
    op.create_table('dapp_submission',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('url', sa.String(length=80), nullable=False),
    sa.Column('address', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('blockchain_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('author', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('logo_path', sa.String(length=100), nullable=False),
    sa.Column('screenshot', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('tagline', sa.String(length=40), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=False),
    sa.Column('whitepaper', sa.String(length=80), nullable=True),
    sa.Column('social_media', postgresql.JSONB(), nullable=False),
    sa.Column('s3_id', postgresql.UUID(), nullable=False),
    sa.Column('status', sa.SmallInteger(), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(), nullable=False),
    sa.Column('launch_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['blockchain_id'], ['blockchain.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['dappest_user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('s3_id'),
    sa.UniqueConstraint('screenshot'),
    sa.UniqueConstraint('whitepaper')
    )
    op.create_table('review',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dapp_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.SmallInteger(), nullable=False),
    sa.Column('title', sa.String(length=50), nullable=False),
    sa.Column('review', sa.Text(), nullable=False),
    sa.Column('feature', postgresql.JSONB(), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['dapp_id'], ['dapp.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['dappest_user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('metric',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dapp_id', sa.Integer(), nullable=False),
    sa.Column('block_interval_id', sa.Integer(), nullable=False),
    sa.Column('data', postgresql.JSONB(), nullable=False),
    sa.ForeignKeyConstraint(['block_interval_id'], ['block_interval.id'], ),
    sa.ForeignKeyConstraint(['dapp_id'], ['dapp.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('ranking',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dapp_id', sa.Integer(), nullable=False),
    sa.Column('block_interval_id', sa.Integer(), nullable=False),
    sa.Column('ranking_name_id', sa.SmallInteger(), nullable=False),
    sa.Column('rank', sa.SmallInteger(), nullable=False),
    sa.ForeignKeyConstraint(['block_interval_id'], ['block_interval.id'], ),
    sa.ForeignKeyConstraint(['dapp_id'], ['dapp.id'], ),
    sa.ForeignKeyConstraint(['ranking_name_id'], ['ranking_name.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('review_like',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dapp_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('review_id', sa.Integer(), nullable=False),
    sa.Column('helpful', sa.SmallInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['dapp_id'], ['dapp.id'], ),
    sa.ForeignKeyConstraint(['review_id'], ['review.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['dappest_user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('user_id', 'review_id', 'helpful')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('review_like')
    op.drop_table('ranking')
    op.drop_table('metric')
    op.drop_table('review')
    op.drop_table('dapp_submission')
    op.drop_table('dapp')
    op.drop_table('dappest_user')
    op.drop_table('block_interval')
    op.drop_table('category')
    op.drop_table('ranking_name')
    op.drop_table('blockchain')
    op.drop_table('daily_item')
    op.drop_table('mailing_list')
    # ### end Alembic commands ###