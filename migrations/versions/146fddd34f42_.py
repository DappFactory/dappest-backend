"""empty message

Revision ID: 146fddd34f42
Revises: 6bf51f2089ca
Create Date: 2018-10-01 06:17:49.216640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '146fddd34f42'
down_revision = '6bf51f2089ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'featured', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'featured', type_='unique')
    # ### end Alembic commands ###
