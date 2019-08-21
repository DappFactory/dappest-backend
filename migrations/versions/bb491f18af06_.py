"""empty message

Revision ID: bb491f18af06
Revises: 1055dd935fca
Create Date: 2018-09-25 15:33:12.666678

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb491f18af06'
down_revision = '1055dd935fca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'contact_form', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'contact_form', type_='unique')
    # ### end Alembic commands ###