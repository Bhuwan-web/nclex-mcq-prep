from sqlalchemy import MetaData, create_engine, func, inspect, select, text
from sqlalchemy.orm import sessionmaker
from mcq_api.models import Base
import os
import shutil

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SEED_DATABASE_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "../data_loader/nclex_simple.db")
)


def default_database_url():
    """Use Vercel's writable scratch directory when running serverlessly."""
    if os.getenv("VERCEL"):
        runtime_database_path = "/tmp/nclex_simple.db"
        if not os.path.exists(runtime_database_path):
            shutil.copyfile(SEED_DATABASE_PATH, runtime_database_path)
        return "sqlite:///" + runtime_database_path

    return "sqlite:///" + SEED_DATABASE_PATH


DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("POSTGRES_URL")
    or os.getenv("POSTGRES_URL_NON_POOLING")
    or default_database_url()
)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite:") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
    # Existing installs predate accounts; keep their sessions while adding the
    # nullable ownership column. New sessions always belong to a user.
    columns = {column["name"] for column in inspect(engine).get_columns("practice_sessions")}
    if "user_id" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE practice_sessions ADD COLUMN user_id INTEGER REFERENCES users(id)")
            )
    if engine.dialect.name == "postgresql":
        _copy_sqlite_data_to_postgres()


def _copy_sqlite_data_to_postgres():
    """Idempotently copy the bundled SQLite database into an empty Postgres DB."""
    from sqlalchemy.dialects.postgresql import insert

    from .models import Base

    source_engine = create_engine("sqlite:///" + SEED_DATABASE_PATH)
    source_metadata = MetaData()
    source_metadata.reflect(bind=source_engine)
    table_order = (
        "questions",
        "detailed_answers",
        "users",
        "practice_sessions",
        "practice_answers",
        "mistakes",
        "user_mistakes",
    )

    try:
        with source_engine.connect() as source, engine.begin() as target:
            # Only one cold-start worker copies rows at a time. Other workers
            # wait, then safely skip the rows already copied by the first.
            target.execute(text("SELECT pg_advisory_xact_lock(87654321098765)"))
            for name in table_order:
                source_table = source_metadata.tables.get(name)
                target_table = Base.metadata.tables.get(name)
                if source_table is None or target_table is None:
                    continue

                shared_columns = [
                    column.name
                    for column in target_table.columns
                    if column.name in source_table.c
                ]
                rows = [
                    {column: row[column] for column in shared_columns}
                    for row in source.execute(select(source_table)).mappings()
                ]
                if rows:
                    target.execute(
                        insert(target_table).values(rows).on_conflict_do_nothing()
                    )

            for table in Base.metadata.sorted_tables:
                if "id" not in table.c:
                    continue
                sequence = target.execute(
                    text("SELECT pg_get_serial_sequence(:table_name, 'id')"),
                    {"table_name": table.name},
                ).scalar()
                if sequence:
                    latest_id = target.execute(select(func.max(table.c.id))).scalar()
                    target.execute(
                        text(
                            "SELECT setval(CAST(:sequence_name AS regclass), :maximum, :is_called)"
                        ),
                        {
                            "sequence_name": sequence,
                            "maximum": latest_id or 1,
                            "is_called": latest_id is not None,
                        },
                    )
    finally:
        source_engine.dispose()


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
