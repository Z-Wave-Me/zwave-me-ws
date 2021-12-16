from dataclasses import dataclass, field
from typing import Union

FIELDS = ["id", "deviceType", "probeType"]
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
        prepared_devices.append(prepared_device)
    return [ZWaveMeData(**d) for d in prepared_devices]
