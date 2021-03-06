"""alter db

Revision ID: 1502d7ef7d40
Revises: None
Create Date: 2016-01-02 21:13:29.296965

"""

# revision identifiers, used by Alembic.
revision = '1502d7ef7d40'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('calculation', sa.Column('contract_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_contract_id_caluclation', 'calculation', 'contract', ['contract_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_contract_id_caluclation', 'calculation', type_='foreignkey')
    op.drop_column('calculation', 'contract_id')
    ### end Alembic commands ###
