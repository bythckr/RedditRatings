"""Add refresh_token column to User model

Revision ID: 3df28505d4eb
Revises: None
Create Date: 2014-05-20 18:21:54.957385

"""

# revision identifiers, used by Alembic.
revision = '3df28505d4eb'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('refresh_token', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'refresh_token')
    ### end Alembic commands ###
