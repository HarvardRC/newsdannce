

from sqlite3 import OperationalError
from app.core.db import TABLE_GLOBAL_STATE, get_db_context
from app.migrations.migration_util import Migration
from app.migrations.v1 import v1
from app.base_logger import logger

migration_list: list[Migration] = [
    v1
]

code_migration_version = len(migration_list)


def get_db_migration_version() -> int:
    with get_db_context() as session:
        curr = session.cursor()
        try:
            row = curr.execute(f"SELECT migration_version FROM {TABLE_GLOBAL_STATE} WHERE id=0").fetchone()
            row = dict(row)
            return row['migration_version']
        except OperationalError as e:
            logger.info("UBALE TO GET MIGRATION VERSION - perhaps migrations have yet been executed?")
            logger.info(f"{e}")
            return -1

def add_migration_version_column():
    with get_db_context() as session:
        curr = session.cursor()
        curr.execute(f"ALTER TABLE {TABLE_GLOBAL_STATE} ADD COLUMN migration_version")
        curr.execute(f"UPDATE {TABLE_GLOBAL_STATE} SET migration_version = 0 WHERE id = 0")
        curr.execute("COMMIT")

def run_migration(migration_number: int, migration_list: list[Migration]):
    idx = migration_number - 1
    if idx < 0:
        raise Exception("Invalid migration index (must not be < 0)")
    migration = migration_list[idx]
    with get_db_context() as session:
        try:
            logger.warning(f"Attempting migration #{migration_number} (idx={idx}) with name={migration.name}")
            curr = session.cursor()
            curr.execute("BEGIN")
            migration.up(curr)
            curr.execute(f"UPDATE {TABLE_GLOBAL_STATE} SET migration_version = ? WHERE id = 0", (migration_number,))
            curr.execute("COMMIT")
            logger.warning(f"Finished migration #{migration_number}")

        except BaseException:
            curr.execute("ROLLBACK")
            raise Exception(f"Unable to complete migration #{migration_number} with name: {migration.name}")


def do_migrations_prestart():
    db_migration_version = get_db_migration_version()
    logger.info(f"CODE MIGRATION VERSION IS {code_migration_version}; DB MIGRATION VERSION IS {db_migration_version}")
    if db_migration_version == -1:
        logger.warning("migration_version field missing. Attempting to add migration_version field to TABLE_GLOBAL_STATE")
        add_migration_version_column()

    while True:
        db_migration_version = get_db_migration_version()
        if db_migration_version < code_migration_version:
            target_migration = db_migration_version + 1
            run_migration(target_migration, migration_list)
        else:
            break

    logger.info("ALL MIGRATIONS COMPLETED")

