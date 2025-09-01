"""Change primary keys to UUID

Revision ID: 20250901_210000
Revises: 185e69f02486
Create Date: 2025-09-01 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '20250901_210000'
down_revision: Union[str, None] = '185e69f02486'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop foreign key constraints first
    op.drop_constraint('auditlog_user_id_fkey', 'auditlog', type_='foreignkey')
    op.drop_constraint('conversationlog_user_id_fkey', 'conversationlog', type_='foreignkey')
    op.drop_constraint('subscription_user_id_fkey', 'subscription', type_='foreignkey')
    op.drop_constraint('usagelog_user_id_fkey', 'usagelog', type_='foreignkey')
    op.drop_constraint('userconsent_user_id_fkey', 'userconsent', type_='foreignkey')

    # Change primary keys to UUID
    op.alter_column('user', 'id', type_=sa.UUID(), postgresql_using='uuid_generate_v4()')
    op.alter_column('finance', 'id', type_=sa.UUID(), postgresql_using='uuid_generate_v4()')
    op.alter_column('subscription', 'id', type_=sa.UUID(), postgresql_using='uuid_generate_v4()')
    op.alter_column('usagelog', 'id', type_=sa.UUID(), postgresql_using='uuid_generate_v4()')
    op.alter_column('userconsent', 'id', type_=sa.UUID(), postgresql_using='uuid_generate_v4()')
    op.alter_column('auditlog', 'id', type_=sa.UUID(), postgresql_using='uuid_generate_v4()')
    op.alter_column('conversationlog', 'id', type_=sa.UUID(), postgresql_using='uuid_generate_v4()')

    # Change foreign keys to UUID
    op.alter_column('subscription', 'user_id', type_=sa.UUID())
    op.alter_column('usagelog', 'user_id', type_=sa.UUID())
    op.alter_column('userconsent', 'user_id', type_=sa.UUID())
    op.alter_column('auditlog', 'user_id', type_=sa.UUID())
    op.alter_column('conversationlog', 'user_id', type_=sa.UUID())

    # Recreate foreign key constraints
    op.create_foreign_key('auditlog_user_id_fkey', 'auditlog', 'user', ['user_id'], ['id'])
    op.create_foreign_key('conversationlog_user_id_fkey', 'conversationlog', 'user', ['user_id'], ['id'])
    op.create_foreign_key('subscription_user_id_fkey', 'subscription', 'user', ['user_id'], ['id'])
    op.create_foreign_key('usagelog_user_id_fkey', 'usagelog', 'user', ['user_id'], ['id'])
    op.create_foreign_key('userconsent_user_id_fkey', 'userconsent', 'user', ['user_id'], ['id'])


def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint('auditlog_user_id_fkey', 'auditlog', type_='foreignkey')
    op.drop_constraint('conversationlog_user_id_fkey', 'conversationlog', type_='foreignkey')
    op.drop_constraint('subscription_user_id_fkey', 'subscription', type_='foreignkey')
    op.drop_constraint('usagelog_user_id_fkey', 'usagelog', type_='foreignkey')
    op.drop_constraint('userconsent_user_id_fkey', 'userconsent', type_='foreignkey')

    # Change back to int
    op.alter_column('user', 'id', type_=sa.Integer())
    op.alter_column('finance', 'id', type_=sa.Integer())
    op.alter_column('subscription', 'id', type_=sa.Integer())
    op.alter_column('usagelog', 'id', type_=sa.Integer())
    op.alter_column('userconsent', 'id', type_=sa.Integer())
    op.alter_column('auditlog', 'id', type_=sa.Integer())
    op.alter_column('conversationlog', 'id', type_=sa.Integer())

    # Change foreign keys back to int
    op.alter_column('subscription', 'user_id', type_=sa.Integer())
    op.alter_column('usagelog', 'user_id', type_=sa.Integer())
    op.alter_column('userconsent', 'user_id', type_=sa.Integer())
    op.alter_column('auditlog', 'user_id', type_=sa.Integer())
    op.alter_column('conversationlog', 'user_id', type_=sa.Integer())

    # Recreate foreign key constraints
    op.create_foreign_key('auditlog_user_id_fkey', 'auditlog', 'user', ['user_id'], ['id'])
    op.create_foreign_key('conversationlog_user_id_fkey', 'conversationlog', 'user', ['user_id'], ['id'])
    op.create_foreign_key('subscription_user_id_fkey', 'subscription', 'user', ['user_id'], ['id'])
    op.create_foreign_key('usagelog_user_id_fkey', 'usagelog', 'user', ['user_id'], ['id'])
    op.create_foreign_key('userconsent_user_id_fkey', 'userconsent', 'user', ['user_id'], ['id'])