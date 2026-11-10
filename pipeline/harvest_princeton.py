import requests
import time
from pathlib import Path

# Stores IDs from API calls
all_ids = []

# Offset that increases each loop
offset = 0

# Loops over Princeton API, storing IDs from results, increasing offset each loop
while True:
    resp = requests.get(
        "https://data.artmuseum.princeton.edu/search",
        params={"q": "dragon", "type": "artobjects", "size": 500, "from": offset},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    for item in data["hits"]["hits"]:
        all_ids.append(item["_id"])
    offset += 500
    time.sleep(0.5)
    if len(all_ids) >= data["hits"]["total"]:
        break

folder = Path(__file__).parent.parent / "data" / "raw" / "princeton"
folder.mkdir(parents=True, exist_ok=True)

for object_id in all_ids:
    path = folder / f"{object_id}.json"
    if path.exists():
        continue
    # attemps API call 3 times before moving on to next ID
    for attempt in range(3):
        try:
            resp = requests.get(
                f"https://data.artmuseum.princeton.edu/objects/{object_id}", timeout=10
            )
            if resp.status_code == 404:
                break
            resp.raise_for_status()

            raw = resp.text
            path.write_text(raw)
            break

        except requests.RequestException as err:
            print(f"failed {object_id}: {err}")
            time.sleep(2**attempt)
    time.sleep(0.75)
