import psycopg
import os
from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).parent.parent

conn = psycopg.connect(os.environ["DATABASE_URL"])

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
                INSERT INTO objects(
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
                    %(id)s,
                    %(museum)s,
                    %(source_id)s,
                    %(title)s,
                    %(artist)s,
                    %(date_display)s,
                    %(date_begin)s,
                    %(date_end)s,
                    %(url)s,
                    %(image_large)s,
                    %(image_small)s,
                    %(medium)s,
                    %(public_domain)s,
                    %(period)s,
                    %(culture)s,
                    %(museum_full_name)s
                ) 
                ON CONFLICT (id) DO UPDATE SET
                    museum = EXCLUDED.museum,
                    source_id = EXCLUDED.source_id,
                    title = EXCLUDED.title,
                    artist = EXCLUDED.artist,
                    date_display = EXCLUDED.date_display,
                    date_begin = EXCLUDED.date_begin,
                    date_end = EXCLUDED.date_end,
                    url = EXCLUDED.url,
                    image_large = EXCLUDED.image_large,
                    image_small = EXCLUDED.image_small,
                    medium = EXCLUDED.medium,
                    public_domain = EXCLUDED.public_domain,
                    period = EXCLUDED.period,
                    culture = EXCLUDED.culture,
                    museum_full_name = EXCLUDED.museum_full_name
                """,
        file_data,
    )
    item_count += 1

conn.commit()

print(f"loaded {item_count} {museum} records")
