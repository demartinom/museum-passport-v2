import sqlite3
from pathlib import Path
import json

REPO_ROOT = Path(__file__).parent.parent

db_path = REPO_ROOT / "data" / "collection.db"

conn = sqlite3.connect(db_path)

conn.execute("""
             CREATE TABLE IF NOT EXISTS objects(
                 id TEXT PRIMARY KEY,
                 museum TEXT,
                 source_id TEXT,
                 title TEXT,
                 artist TEXT,
                 date_display TEXT,
                 date_begin INT,
                 date_end INT,
                 url TEXT,
                 image_large TEXT,
                 image_small TEXT,
                 medium TEXT,
                 public_domain BOOLEAN
                 
             )
             """)

file_path = REPO_ROOT / "data" / "normalized" / "met" / "49925.json"
file_text = file_path.read_text()
file_data = json.loads(file_text)

conn.execute(
    """
             INSERT OR REPLACE INTO objects(
                 id,
                museum,
                source_id,
                title,
                artist,
                date_display,
                date_begin,
                date_end,
                url,
                image_large,
                image_small,
                medium,
                public_domain
             ) VALUES(
                :id,
                :museum,
                :source_id,
                :title,
                :artist,
                :date_display,
                :date_begin,
                :date_end,
                :url,
                :image_large,
                :image_small,
                :medium,
                :public_domain
             )
             """,
    file_data,
)

conn.commit()
