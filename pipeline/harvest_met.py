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

resp = requests.get(
    f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{all_ids[0]}"
)
resp.raise_for_status()

raw = resp.text

folder = Path(__file__).parent.parent / "data" / "raw" / "met"
folder.mkdir(parents=True, exist_ok=True)
(folder / f"{all_ids[0]}.json").write_text(raw)
