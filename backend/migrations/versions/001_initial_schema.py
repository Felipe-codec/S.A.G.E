"""Initial schema with all tables and indexes

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-04 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Identificadores da revisão
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tabela: sellers
    op.create_table(
        'sellers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sellers_id', 'sellers', ['id'], unique=False)
    op.create_index('ix_sellers_email', 'sellers', ['email'], unique=True)

    # 2. Tabela: imap_configs
    op.create_table(
        'imap_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('host', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False, server_default=sa.text('993')),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('encrypted_password', sa.Text(), nullable=False),
        sa.Column('use_ssl', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_imap_configs_id', 'imap_configs', ['id'], unique=False)
    op.create_index('ix_imap_configs_seller_id', 'imap_configs', ['seller_id'], unique=False)

    # 3. Tabela: steam_accounts
    op.create_table(
        'steam_accounts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_steam_accounts_id', 'steam_accounts', ['id'], unique=False)
    op.create_index('ix_steam_accounts_seller_id', 'steam_accounts', ['seller_id'], unique=False)
    op.create_index('ix_steam_accounts_username', 'steam_accounts', ['username'], unique=False)
    op.create_index('ix_steam_accounts_seller_username', 'steam_accounts', ['seller_id', 'username'], unique=False)

    # 4. Tabela: redemption_tokens
    op.create_table(
        'redemption_tokens',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('steam_account_id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('max_uses', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('current_uses', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['steam_account_id'], ['steam_accounts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_redemption_tokens_id', 'redemption_tokens', ['id'], unique=False)
    op.create_index('ix_redemption_tokens_seller_id', 'redemption_tokens', ['seller_id'], unique=False)
    op.create_index('ix_redemption_tokens_steam_account_id', 'redemption_tokens', ['steam_account_id'], unique=False)
    op.create_index('ix_redemption_tokens_token_hash', 'redemption_tokens', ['token_hash'], unique=True)
    op.create_index('ix_redemption_tokens_expires_at', 'redemption_tokens', ['expires_at'], unique=False)
    op.create_index('ix_redemption_tokens_account_expires', 'redemption_tokens', ['steam_account_id', 'expires_at'], unique=False)

    # 5. Tabela: redemption_sessions
    op.create_table(
        'redemption_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('token_id', sa.Integer(), nullable=False),
        sa.Column('session_identifier_hash', sa.String(length=64), nullable=False),
        sa.Column('ip_address_masked', sa.String(length=64), nullable=False),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['token_id'], ['redemption_tokens.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_redemption_sessions_id', 'redemption_sessions', ['id'], unique=False)
    op.create_index('ix_redemption_sessions_token_id', 'redemption_sessions', ['token_id'], unique=False)
    op.create_index('ix_redemption_sessions_session_hash', 'redemption_sessions', ['session_identifier_hash'], unique=False)

    # 6. Tabela: code_requests
    op.create_table(
        'code_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('steam_account_id', sa.Integer(), nullable=False),
        sa.Column('token_id', sa.Integer(), nullable=False),
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('code_found_masked', sa.String(length=10), nullable=True),
        sa.Column('search_duration_ms', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['steam_account_id'], ['steam_accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['token_id'], ['redemption_tokens.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_code_requests_id', 'code_requests', ['id'], unique=False)
    op.create_index('ix_code_requests_steam_account_id', 'code_requests', ['steam_account_id'], unique=False)
    op.create_index('ix_code_requests_token_id', 'code_requests', ['token_id'], unique=False)
    op.create_index('ix_code_requests_requested_at', 'code_requests', ['requested_at'], unique=False)
    op.create_index('ix_code_requests_account_requested', 'code_requests', ['steam_account_id', 'requested_at'], unique=False)

    # 7. Tabela: access_logs
    op.create_table(
        'access_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=True),
        sa.Column('request_id', sa.String(length=64), nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('ip_masked', sa.String(length=64), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_access_logs_id', 'access_logs', ['id'], unique=False)
    op.create_index('ix_access_logs_seller_id', 'access_logs', ['seller_id'], unique=False)
    op.create_index('ix_access_logs_request_id', 'access_logs', ['request_id'], unique=False)
    op.create_index('ix_access_logs_created_at', 'access_logs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('access_logs')
    op.drop_table('code_requests')
    op.drop_table('redemption_sessions')
    op.drop_table('redemption_tokens')
    op.drop_table('steam_accounts')
    op.drop_table('imap_configs')
    op.drop_table('sellers')
