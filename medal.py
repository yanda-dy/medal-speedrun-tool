import json
from dataclasses import dataclass

@dataclass
class Medal:
    id: int
    name: str
    description: str
    restriction: str
    grouping: str

with open("data/medal_data.json", "r") as f:
    medal_json = json.load(f)

medals = {
    medal["MedalID"]: Medal(
        id=medal["MedalID"],
        name=medal["Name"],
        description=medal["Description"],
        restriction=medal["Restriction"],
        grouping=medal["Grouping"]
    ) for medal in medal_json
}

pack_data = json.load(open("data/pack_data.json", "r"))
packs = {
    int(pack["medalid"]): pack["packs"] for pack in pack_data
}

aeon_maps = set(json.load(open("data/aeon_maps.json", "r")))
