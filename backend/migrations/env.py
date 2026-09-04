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

# Determina a URL correta para o Alembic:
# 1. Se o config já tiver uma URL customizada passada explicitamente (ex: testes com sqlite)
# 2. Caso contrário, utiliza DATABASE_URL do ambiente ou settings.DATABASE_URL
cfg_url = config.get_main_option("sqlalchemy.url")
if cfg_url and ("sqlite" in cfg_url or ":memory:" in cfg_url):
    database_url = cfg_url
else:
    import os
    database_url = os.environ.get("DATABASE_URL") or settings.DATABASE_URL

# Normaliza postgres:// para postgresql:// e codifica caracteres como @ na senha
if database_url and isinstance(database_url, str):
    database_url = database_url.strip()
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    import re, urllib.parse
    match = re.match(r'^(postgresql(?:\+[a-z0-9]+)?://)([^:]+):(.*)@([^/@:]+(?::\d+)?(?:/.*)?)$', database_url)
    if match:
        scheme, user, raw_pwd, rest = match.groups()
        decoded_pwd = urllib.parse.unquote(raw_pwd)
        quoted_pwd = urllib.parse.quote(decoded_pwd, safe="")
        database_url = f"{scheme}{user}:{quoted_pwd}@{rest}"

# No configparser do Alembic, o '%' deve ser escapado como '%%' para não disparar erro de interpolação
escaped_url = database_url.replace("%", "%%")
config.set_main_option("sqlalchemy.url", escaped_url)


def run_migrations_offline() -> None:
    """Executa migrações no modo 'offline' sem abrir conexão real."""
    url = config.get_main_option("sqlalchemy.url") or database_url
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
    url = config.get_main_option("sqlalchemy.url") or database_url
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
