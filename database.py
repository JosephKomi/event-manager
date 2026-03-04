import aiosqlite
import os
from dotenv import load_dotenv

# Charge les variables du fichier .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "./events.db")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id              TEXT PRIMARY KEY,
    event_type      TEXT NOT NULL,
    source_service  TEXT NOT NULL,
    payload         TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'PENDING',
    retry_count     INTEGER NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME NOT NULL
);
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_status ON events (status);
CREATE INDEX IF NOT EXISTS idx_event_type ON events (event_type);
CREATE INDEX IF NOT EXISTS idx_source_service ON events (source_service);
"""


async def get_db():
    """Retourne une connexion a la base de donnees."""
    db = await aiosqlite.connect(DATABASE_URL)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


async def init_db():
    """Cree la table events et les index si ils n'existent pas."""
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(CREATE_TABLE_SQL)
        # Les index s'executent separement
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_status ON events (status);"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_event_type ON events (event_type);"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_source_service ON events (source_service);"
        )
        await db.commit()
        print("Base de donnees initialisee avec succes")