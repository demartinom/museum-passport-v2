import requests

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
    data = resp.json()
    all_ids.extend(data["objectIDs"])
    offset += 100
    if len(all_ids) >= 1000:
        break

print(f"Length:{len(all_ids)}, IDs:{all_ids}")
