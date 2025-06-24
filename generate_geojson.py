import os
from collections import defaultdict
from shapely.geometry import mapping
from shapely.geometry import Point
import json

YEAR = os.environ["YEAR"]

types = defaultdict(list)

with open(f"data/{YEAR}/raw/map_pois.json") as f:
    poi_json = json.load(f)

for item in poi_json["documents"]:
    item = item["fields"]

    tags = []
    if "arrayValue" in item["tags"]:
        tags = [t["stringValue"] for t in item["tags"]["arrayValue"]["values"]]

    p = mapping(
        Point(
            item["point"]["geoPointValue"]["longitude"],
            item["point"]["geoPointValue"]["latitude"],
        )
    )
    types[item["type"]["stringValue"]].append(
        {
            "type": "Feature",
            "properties": {
                "name": item["name"]["stringValue"],
                "description": item["description"].get("stringValue", None),
                "tags": tags,
                "is_in_market": item["isInMarket"]["booleanValue"],
                "is_busy": item["isBusy"]["booleanValue"],
                "busy_title": item["busyTitle"].get("StringValue", None),
                "busy_description": item["busyDescription"].get("StringValue", None),
                "display_on_map": item["displayOnMap"]["booleanValue"],
            },
            "geometry": p,
        }
    )

path = f"data/{YEAR}/geojson/"
try:
    os.makedirs(path)
except FileExistsError:
    pass

for type_name, features in types.items():
    schema = {
        "type": "FeatureCollection",
        "features": features,
    }
    with open(path + f"{type_name}.geojson", "w") as outfile:
        outfile.write(json.dumps(schema, indent=4))
