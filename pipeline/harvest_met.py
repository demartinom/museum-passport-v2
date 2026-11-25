import requests
import time
from pathlib import Path
from datetime import date

# Raw Met files, plus the harvester's two state files
MET_DIR = Path(__file__).parent.parent / "data" / "raw" / "met"
LAST_RUN_PATH = MET_DIR / "last_run.txt"
NOT_FOUND_PATH = MET_DIR / "not_found.txt"


def search_ids() -> list[int]:
    # Stores IDs from API calls
    all_ids = []

    # Offset that increases each loop
    offset = 0

    # Loops over Met API, increasing offset each loop
    while True:
        resp = requests.get(
            "https://collectionapi.metmuseum.org/public/collection/v1.1/search",
            params={
                "q": "porcelain",
                "departmentId": 6,
                "limit": 100,
                "offset": offset,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        all_ids.extend(data["objectIDs"])
        offset += 100
        time.sleep(0.5)
        if len(all_ids) >= data["total"]:
            break
    return all_ids


def find_last_run_date(last_run_path: Path) -> str:
    # if last_run.txt doesn't exist, set last run to today
    last_run = str(date.today())
    if last_run_path.exists():
        last_run = last_run_path.read_text().strip()
    return last_run


def find_refetch_ids(last_run_date: str, all_ids: list[int]) -> set[int]:
    # Find IDs that have changed since last run
    resp = requests.get(
        "https://collectionapi.metmuseum.org/public/collection/v1/objects",
        params={"metadataDate": last_run_date},
        timeout=10,
    )
    resp.raise_for_status()
    changed_data = resp.json()

    # Create empty set if not changed IDs
    changed_ids = set(changed_data["objectIDs"] or [])

    # List of items that have changed and need to be refetched
    to_refetch = changed_ids & set(all_ids)
    print(f"Need to refetch {len(to_refetch)} items")
    return to_refetch


def read_not_found(not_found_path: Path) -> set[str]:
    # Reads list of IDs that returned 404
    not_found = set()
    if not_found_path.exists():
        not_found = set(not_found_path.read_text().split())
    return not_found


def download_object(object_id: int, path: Path, not_found_path: Path) -> bool:
    # attemps API call 3 times before moving on to next ID
    for attempt in range(3):
        try:
            resp = requests.get(
                f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}",
                timeout=10,
            )
            if resp.status_code == 404:
                with open(not_found_path, "a") as f:
                    f.write(f"{object_id}\n")
                return False
            resp.raise_for_status()

            raw = resp.text
            path.write_text(raw)
            return True

        except requests.RequestException as err:
            print(f"failed {object_id}: {err}")
            time.sleep(2**attempt)
    return False


def main():
    item_count = 0
    MET_DIR.mkdir(parents=True, exist_ok=True)

    all_ids = search_ids()
    last_run_date = find_last_run_date(LAST_RUN_PATH)
    to_refetch = find_refetch_ids(last_run_date, all_ids)
    not_found_ids = read_not_found(NOT_FOUND_PATH)
    for object_id in all_ids:
        path = MET_DIR / f"{object_id}.json"

        # Skip objects already fetched unless the Met changed them since the last run
        if path.exists() and object_id not in to_refetch:
            continue

        # Checks if object_id is in list of not found IDs and skips
        if str(object_id) in not_found_ids:
            continue
        if download_object(object_id, path, NOT_FOUND_PATH):
            item_count += 1
            print(f"Downloaded {item_count} records", end="\r", flush=True)
        time.sleep(0.5)

    # Write file containing date when last ran
    LAST_RUN_PATH.write_text(str(date.today()))

    print(f"Search found {len(all_ids)}, downloaded {item_count} Met records")


if __name__ == "__main__":
    main()
