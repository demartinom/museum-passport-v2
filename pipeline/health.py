import sqlite3
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).parent.parent

errors = []

db_path = REPO_ROOT / "data" / "collection.db"

conn = sqlite3.connect(db_path)

# Checks if a museum has fewer than expected items in database
res_totals = conn.execute("""
             SELECT museum as "Museum",
             COUNT(*) AS "Total Objects"
             FROM objects GROUP BY museum
             """)

totals = {}

minimums = {"met": 1500, "princeton": 200}
for museum, total in res_totals.fetchall():
    totals[museum] = total

for museum, minimum in minimums.items():
    total = totals.get(museum, 0)

    if total < minimum:
        errors.append(f"{museum} has {total} items, expected at least {minimum} items")

# Checks if any item is missing a title
res_empty_title = conn.execute("""
                               SELECT COUNT(*) from objects 
                               WHERE title = '' 
                               OR title is NULL
                               """)

missing_titles = res_empty_title.fetchone()[0]

if missing_titles > 0:
    errors.append(f"{missing_titles} items with no name")

if not errors:
    print("All checks passed")
else:
    for error in errors:
        print(error)
    sys.exit(1)
