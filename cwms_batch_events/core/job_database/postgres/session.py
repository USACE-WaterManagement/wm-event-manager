from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from cwms_batch_events.core.settings import settings

db_url = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.pguser,
    password=settings.pgpassword,
    database=settings.pgdatabase,
    host=settings.pghost,
    query=(
        {"options": f"-csearch_path={settings.pgschema}"}
        if settings.pgschema
        else {}
    ),
)

engine = create_engine(db_url)

SessionLocal = sessionmaker(engine)


def create_session():
    return SessionLocal()
