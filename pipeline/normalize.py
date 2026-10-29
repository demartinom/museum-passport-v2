import yaml
from pathlib import Path
import json

mapping_path = Path(__file__).parent / "mappings" / "met.yaml"
yaml_text = mapping_path.read_text()
mapping = yaml.safe_load(yaml_text)

raw_path = Path(__file__).parent.parent / "data" / "raw" / "met" / "49925.json"
raw_text = raw_path.read_text()

raw = json.loads(raw_text)

record = {}

for my_field, met_field in mapping.items():
    record[my_field] = raw[met_field]
