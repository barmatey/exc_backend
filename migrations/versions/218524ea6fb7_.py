"""empty message

Revision ID: 218524ea6fb7
Revises: 71128da45144
Create Date: 2023-11-16 13:46:24.558071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '218524ea6fb7'
down_revision: Union[str, None] = '71128da45144'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('commodity',
    sa.Column('ticker', sa.String(length=16), nullable=False),
    sa.Column('description', sa.String(length=2048), nullable=False),
    sa.Column('specification', sa.String(length=2048), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ticker')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('commodity')
    # ### end Alembic commands ###
