from dataclasses import dataclass, field
from typing import Union

FIELDS = [
    "id",
    "deviceType",
    "probeType",
    "locationName",
    "manufacturer",
    "firmware",
    "tags",
    "creatorId",
    "nodeId"
]
METRICS_SCALE = ["title", "level", "scaleTitle", "min", "max", "color", "isFailed"]
TYPE_LIGHT = "type-light"


@dataclass
class ZWaveMeData:
    id: str
    deviceType: str
    title: str
    level: Union[str, int, float]
    deviceIdentifier: str
    probeType: str = ""
    scaleTitle: str = ""
    min: str = ""
    max: str = ""
    color: dict = field(default_factory=dict)
    isFailed: bool = False
    locationName: str = ""
    manufacturer: str = ""
    firmware: str = ""
    tags: list[str] = field(default_factory=list)
    nodeId: str = ""
    creatorId: str = ""

def prepare_devices(devices: list[dict]) -> list[ZWaveMeData]:
    prepared_devices = []
    for device in devices:
        prepared_device = {
            **{key: device[key] for key in FIELDS if key in device},
            **{
                key: device["metrics"][key]
                for key in METRICS_SCALE
                if key in device["metrics"]
            },
        }
        prepared_device = set_device_type(prepared_device)
        if "creatorId" in prepared_device and "nodeId" in prepared_device:
            prepared_device[
                "deviceIdentifier"] = f"{prepared_device['creatorId']}_{prepared_device['nodeId']}"
        else:
            prepared_device["deviceIdentifier"] = prepared_device["id"]
        prepared_devices.append(prepared_device)
    return [ZWaveMeData(**d) for d in prepared_devices]


def set_device_type(prepared_device):
    if prepared_device["probeType"] == "siren":
        prepared_device["deviceType"] = "siren"
    elif TYPE_LIGHT in prepared_device["tags"] and prepared_device[
        "deviceType"
    ] not in ["switchRGB", "switchRGBW"]:
        prepared_device["deviceType"] = "lightMultilevel"
        prepared_device["color"] = {
            "r": round(2.55 * float(prepared_device["level"])),
            "g": round(2.55 * float(prepared_device["level"])),
            "b": round(2.55 * float(prepared_device["level"])),
        }
        prepared_device["level"] = (
            "on" if float(prepared_device["level"]) > 0 else "off"
        )
    elif prepared_device["probeType"] == "motor":
        prepared_device["deviceType"] = "motor"
    elif prepared_device["probeType"] == "fan":
        prepared_device["deviceType"] = "fan"
    return prepared_device
