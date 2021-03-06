from dataclasses import dataclass, field
from typing import Union

FIELDS = ["id", "deviceType", "probeType", "locationName", "manufacturer",
          "firmware"]
METRICS_SCALE = ["title", "level", "scaleTitle", "min", "max", "color",
                 "isFailed"]


@dataclass
class ZWaveMeData:
    id: str
    deviceType: str
    title: str
    level: Union[str, int, float]
    probeType: str = ""
    scaleTitle: str = ""
    min: str = ""
    max: str = ""
    color: dict = field(default_factory=dict)
    isFailed: bool = False
    locationName: str = ""
    manufacturer: str = ""
    firmware: str = ""


def prepare_devices(devices: list) -> list:
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
        if prepared_device["probeType"] == "siren":
            prepared_device["deviceType"] = "siren"
        elif prepared_device["probeType"] == "motor":
            prepared_device["deviceType"] = "motor"
        elif prepared_device["probeType"] == "fan":
            prepared_device["deviceType"] = "fan"
        prepared_devices.append(prepared_device)
    return [ZWaveMeData(**d) for d in prepared_devices]
