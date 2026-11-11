import sqlite3
from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).parent.parent

db_path = REPO_ROOT / "data" / "collection.db"

conn = sqlite3.connect(db_path)

conn.execute("""
             CREATE TABLE IF NOT EXISTS objects(
                 id TEXT PRIMARY KEY,
                 museum TEXT,
                 museum_full_name TEXT,
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
                 public_domain BOOLEAN,
                 period TEXT,
                 culture TEXT
                 
             )
             """)

museum = sys.argv[1]
item_count = 0

normalized_dir = REPO_ROOT / "data" / "normalized" / museum
for file_path in normalized_dir.glob("*.json"):
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
                    public_domain,
                    period,
                    culture,
                    museum_full_name
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
                    :public_domain,
                    :period,
                    :culture,
                    :museum_full_name
                )
                """,
        file_data,
    )
    item_count += 1

print(f"loaded {item_count} {museum} records")

conn.commit()
