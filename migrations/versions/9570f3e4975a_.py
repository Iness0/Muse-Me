"""empty message

Revision ID: 9570f3e4975a
Revises: 601e00b117c4
Create Date: 2023-03-30 09:57:18.633122

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9570f3e4975a'
down_revision = '601e00b117c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('posts_ibfk_2', 'posts', type_='foreignkey')
    op.drop_column('posts', 'image_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('image_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('posts_ibfk_2', 'posts', 'images', ['image_id'], ['id'])
    # ### end Alembic commands ###