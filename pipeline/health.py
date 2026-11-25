import sqlite3
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).parent.parent

errors = []

db_path = REPO_ROOT / "data" / "collection.db"

conn = sqlite3.connect(db_path)

conn.execute("""
             CREATE TABLE IF NOT EXISTS count_history(
                 museum TEXT,
                 count INT,
                 run_at TEXT DEFAULT CURRENT_TIMESTAMP
             )
             """)

# Fails if a museum's count dropped more than 10% since the last passing run
res_totals = conn.execute("""
             SELECT museum ,
             COUNT(*) 
             FROM objects GROUP BY museum
             """)

totals = {}

for museum, total in res_totals.fetchall():
    totals[museum] = total


for museum, total in totals.items():
    res_last_totals = conn.execute(
        """
                              SELECT count
                              FROM count_history WHERE museum = ? 
                              ORDER BY rowid DESC
                              LIMIT 1
                              """,
        (museum,),
    )
    last_row = res_last_totals.fetchone()
    if last_row is not None:
        last_total = last_row[0]
        minimum_total = last_total * 0.9
        if total < minimum_total:
            errors.append(
                f"{museum} has {total} items, expected at least {int(minimum_total)} items"
            )

# Checks if any item is missing a title
res_empty_title = conn.execute("""
                               SELECT COUNT(*) from objects 
                               WHERE title = '' 
                               OR title is NULL
                               """)

missing_titles = res_empty_title.fetchone()[0]

if missing_titles > 0:
    errors.append(f"{missing_titles} items with no name")

# Checks if any item has a date_begin of 0
res_bad_date_begin = conn.execute("""
                               SELECT COUNT(*) from objects
                               WHERE date_begin = 0
                               """)

bad_date_begin = res_bad_date_begin.fetchone()[0]

if bad_date_begin > 0:
    errors.append(f"{bad_date_begin} items with a date_begin of 0")

# Checks if any item is missing a url
res_missing_url = conn.execute("""
                               SELECT COUNT(*) from objects
                               WHERE url = ''
                               OR url is NULL
                               """)

missing_url = res_missing_url.fetchone()[0]

if missing_url > 0:
    errors.append(f"{missing_url} items with no url")


# Checks if any item has a date_begin later than date_end
res_incorrect_date_begin = conn.execute("""
                                     SELECT COUNT(*) from objects
                                     WHERE date_begin > date_end
                                    """)

incorrect_date_begin = res_incorrect_date_begin.fetchone()[0]

if incorrect_date_begin > 0:
    errors.append(
        f"{incorrect_date_begin} items where date_begin is later than date_end"
    )

# Checks if any non public-domain item has images
res_restricted_images = conn.execute("""
                                     SELECT COUNT(*) from objects
                                     WHERE (image_large is NOT NULL
                                     OR image_small is NOT NULL)
                                     AND public_domain IS NOT 1
                                     """)

restricted_images = res_restricted_images.fetchone()[0]
if restricted_images > 0:
    errors.append(f"{restricted_images} restricted objects still have image links")


if not errors:
    for museum, total in totals.items():
        conn.execute(
            "INSERT INTO count_history (museum, count) VALUES (?,?)",
            (museum, total),
        )
    conn.commit()
    print("All checks passed")
else:
    for error in errors:
        print(error)
    sys.exit(1)
