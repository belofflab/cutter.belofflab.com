"""update arch

Revision ID: 5810488c307a
Revises: 2a5184102780
Create Date: 2024-02-21 14:17:40.166282

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5810488c307a'
down_revision = '2a5184102780'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'shortcuts', ['code'])
    op.drop_constraint('shortcuts_clients_client_id_fkey', 'shortcuts_clients', type_='foreignkey')
    op.drop_constraint('shortcuts_clients_shortcut_id_fkey', 'shortcuts_clients', type_='foreignkey')
    op.create_foreign_key(None, 'shortcuts_clients', 'forwarding_clients', ['client_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'shortcuts_clients', 'shortcuts', ['shortcut_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('users_shortcuts_shortcut_id_fkey', 'users_shortcuts', type_='foreignkey')
    op.create_foreign_key(None, 'users_shortcuts', 'shortcuts', ['shortcut_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users_shortcuts', type_='foreignkey')
    op.create_foreign_key('users_shortcuts_shortcut_id_fkey', 'users_shortcuts', 'shortcuts', ['shortcut_id'], ['id'])
    op.drop_constraint(None, 'shortcuts_clients', type_='foreignkey')
    op.drop_constraint(None, 'shortcuts_clients', type_='foreignkey')
    op.create_foreign_key('shortcuts_clients_shortcut_id_fkey', 'shortcuts_clients', 'shortcuts', ['shortcut_id'], ['id'])
    op.create_foreign_key('shortcuts_clients_client_id_fkey', 'shortcuts_clients', 'forwarding_clients', ['client_id'], ['id'])
    op.drop_constraint(None, 'shortcuts', type_='unique')
    # ### end Alembic commands ###
