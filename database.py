import aiosqlite
import os
from dotenv import load_dotenv

# Charge les variables du fichier .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "./events.db")

# Requête de création de la table events
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id           TEXT PRIMARY KEY,
    event_type   TEXT NOT NULL,
    source_service TEXT NOT NULL,
    payload      TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'PENDING',
    retry_count  INTEGER NOT NULL DEFAULT 0,
    created_at   DATETIME NOT NULL,
    updated_at   DATETIME NOT NULL
);
"""

async def get_db():
    """Retourne une connexion à la base de données."""
    db = await aiosqlite.connect(DATABASE_URL)
    db.row_factory = aiosqlite.Row  
    try:
        yield db
    finally:
        await db.close()


async def init_db():
    """Crée la table events si elle n'existe pas."""
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()
        print(f" Base de données initialisée : {DATABASE_URL}")