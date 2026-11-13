import sqlite3
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).parent.parent

db_path = REPO_ROOT / "data" / "collection.db"

conn = sqlite3.connect(db_path)

res = conn.execute("""
             SELECT museum as "Museum",
             COUNT(*) AS "Total Objects"
             FROM objects GROUP BY museum
             """)

totals = {}

minimums = {"met": 1500, "princeton": 200}
for museum, total in res.fetchall():
    totals[museum] = total

for museum, minimum in minimums.items():
    total = totals.get(museum, 0)

    if total < minimum:
        print(f"{museum} has {total} items, expected at least {minimum} items")
        sys.exit(1)

print("All checks passed")
