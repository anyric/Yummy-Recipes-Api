"""empty message

Revision ID: 72830298ad15
Revises: f73cd9f4b495
Create Date: 2018-01-08 01:27:51.874338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72830298ad15'
down_revision = 'f73cd9f4b495'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('date_blacklisted', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blacklist')
    # ### end Alembic commands ###