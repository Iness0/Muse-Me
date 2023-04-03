"""empty message

Revision ID: 66882a16c715
Revises: 8485b47b202b
Create Date: 2023-03-24 14:53:47.647279

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66882a16c715'
down_revision = '8485b47b202b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('emoji', sa.String(length=20), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reactions')
    # ### end Alembic commands ###
