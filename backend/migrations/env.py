import sys
from logging.config import fileConfig
from pathlib import Path
from alembic import context
from sqlalchemy import engine_from_config, pool

# Adiciona o diretório raiz do backend ao sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.db.base import Base
# Importa todos os modelos para registro de metadados
import app.models

# Objeto de configuração do Alembic
config = context.config

# Interpreta o arquivo de configuração para logging Python
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define o target_metadata para suporte a autogenerate
target_metadata = Base.metadata

# Define a URL do banco a partir da variável de ambiente caso não tenha sido passada explicitamente
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Executa migrações no modo 'offline' sem abrir conexão real."""
    url = config.get_main_option("sqlalchemy.url") or settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrações no modo 'online' conectando ao banco de dados."""
    url = config.get_main_option("sqlalchemy.url") or settings.DATABASE_URL
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
