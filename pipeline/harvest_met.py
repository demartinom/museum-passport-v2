import requests
import time
from pathlib import Path

# Stores IDs from API calls
all_ids = []

# Offset that increases each loop
offset = 0

# Loops over Met API, increasing offset each loop
while True:
    resp = requests.get(
        "https://collectionapi.metmuseum.org/public/collection/v1.1/search",
        params={"q": "porcelain", "departmentId": 6, "limit": 100, "offset": offset},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    all_ids.extend(data["objectIDs"])
    offset += 100
    time.sleep(0.5)
    if len(all_ids) >= data["total"]:
        break

folder = Path(__file__).parent.parent / "data" / "raw" / "met"
folder.mkdir(parents=True, exist_ok=True)

item_count = 0

# Reads list of IDs that returned 404
not_found = set()
not_found_path = folder / "not_found.txt"
if not_found_path.exists():
    not_found = set(not_found_path.read_text().split())

for object_id in all_ids:
    path = folder / f"{object_id}.json"
    if path.exists():
        continue
    # Checks if object_id is in list of not found IDs and skips
    if str(object_id) in not_found:
        continue
    # attemps API call 3 times before moving on to next ID
    for attempt in range(3):
        try:
            resp = requests.get(
                f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}",
                timeout=10,
            )
            if resp.status_code == 404:
                with open(folder / "not_found.txt", "a") as f:
                    f.write(f"{object_id}\n")
                break
            resp.raise_for_status()

            raw = resp.text
            path.write_text(raw)
            item_count += 1
            print(f"Downloaded {item_count} new records", end="\r", flush=True)
            break

        except requests.RequestException as err:
            print(f"failed {object_id}: {err}")
            time.sleep(2**attempt)

    time.sleep(0.5)

print(f"Search found {len(all_ids)}, downloaded {item_count} new Met records")
