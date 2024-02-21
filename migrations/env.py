from logging.config import fileConfig

from data.config import DATABASE_URL
from sqlalchemy import create_engine
from database.models import db

from alembic import context

config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = db




def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            compare_type=True

        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()