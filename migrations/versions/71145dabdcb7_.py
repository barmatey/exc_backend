"""empty message

Revision ID: 71145dabdcb7
Revises: caf9646b2ca8
Create Date: 2023-11-28 21:25:33.811927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '71145dabdcb7'
down_revision: Union[str, None] = 'caf9646b2ca8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('association_table',
    sa.Column('trs_id', sa.Uuid(), nullable=True),
    sa.Column('deal_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['deal_id'], ['deal_table.id'], ),
    sa.ForeignKeyConstraint(['trs_id'], ['transaction.id'], )
    )
    op.drop_table('deal_transaction_table')
    op.add_column('deal_table', sa.Column('weighted_price', sa.Float(), nullable=False))
    op.add_column('deal_table', sa.Column('total_quantity', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('deal_table', 'total_quantity')
    op.drop_column('deal_table', 'weighted_price')
    op.create_table('deal_transaction_table',
    sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('direction', sa.VARCHAR(length=8), autoincrement=False, nullable=False),
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('deal_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['deal_id'], ['deal_table.id'], name='deal_transaction_table_deal_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='deal_transaction_table_pkey')
    )
    op.drop_table('association_table')
    # ### end Alembic commands ###