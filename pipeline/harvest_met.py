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
    if len(all_ids) >= 1000:
        break

folder = Path(__file__).parent.parent / "data" / "raw" / "met"
folder.mkdir(parents=True, exist_ok=True)

for object_id in all_ids:
    path = folder / f"{object_id}.json"
    if path.exists():
        continue
    # attemps API call 3 times before moving on to next ID
    for attempt in range(3):
        try:
            resp = requests.get(
                f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}",
                timeout=10,
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

    time.sleep(1)
