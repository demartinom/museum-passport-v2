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
not_found = []
for object_id in all_ids:
    path = folder / f"{object_id}.json"
    if path.exists():
        continue
    resp = requests.get(
        f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    )
    if resp.status_code == 404:
        not_found.append(object_id)
        time.sleep(1)
        continue
    resp.raise_for_status()
    raw = resp.text
    (folder / f"{object_id}.json").write_text(raw)
    time.sleep(1)

print("IDs not found")
for object_id in not_found:
    print(f"{id}")
