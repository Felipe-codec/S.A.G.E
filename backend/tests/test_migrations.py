from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_migrations_upgrade_and_indexes():
    """Valida a execução real de 'alembic upgrade head' e a existência de todos os índices requeridos."""
    # Cria banco SQLite temporário para teste da migração
    db_file = Path("test_migration.db")
    if db_file.exists():
        db_file.unlink()

    db_url = f"sqlite:///{db_file.absolute()}"

    ini_path = Path(__file__).resolve().parent.parent / "alembic.ini"
    alembic_cfg = Config(str(ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    try:
        # Executa a migração
        command.upgrade(alembic_cfg, "head")

        engine = create_engine(db_url)
        inspector = inspect(engine)

        tables = inspector.get_table_names()
        expected_tables = [
            "sellers",
            "imap_configs",
            "steam_accounts",
            "redemption_tokens",
            "redemption_sessions",
            "code_requests",
            "access_logs",
        ]
        for tbl in expected_tables:
            assert tbl in tables, f"Tabela esperada {tbl} não encontrada após migração"

        # Valida índices específicos requeridos
        steam_indices = [idx["name"] for idx in inspector.get_indexes("steam_accounts")]
        assert "ix_steam_accounts_seller_id" in steam_indices
        assert "ix_steam_accounts_username" in steam_indices

        token_indices = [idx["name"] for idx in inspector.get_indexes("redemption_tokens")]
        assert "ix_redemption_tokens_token_hash" in token_indices
        assert "ix_redemption_tokens_steam_account_id" in token_indices
        assert "ix_redemption_tokens_expires_at" in token_indices

        session_indices = [idx["name"] for idx in inspector.get_indexes("redemption_sessions")]
        assert "ix_redemption_sessions_token_id" in session_indices

        code_indices = [idx["name"] for idx in inspector.get_indexes("code_requests")]
        assert "ix_code_requests_steam_account_id" in code_indices
        assert "ix_code_requests_requested_at" in code_indices

        access_indices = [idx["name"] for idx in inspector.get_indexes("access_logs")]
        assert "ix_access_logs_seller_id" in access_indices

        engine.dispose()
    finally:
        if db_file.exists():
            try:
                db_file.unlink()
            except Exception:
                pass
