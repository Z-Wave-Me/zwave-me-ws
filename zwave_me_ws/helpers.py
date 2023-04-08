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
    "nodeId",
]
METRICS_SCALE = ["title", "level", "scaleTitle", "min", "max", "color", "isFailed"]

TYPE_TAGS = {
    'type-sensor-binary': "sensorBinary",
    'type-light': "lightMultilevel",
    'type-button': "toggleButton",
    'type-thermostat': "thermostat",
    'type-motor': "motor",
    'type-fan': "fan",
    'type-doorlock': "doorlock",
    'type-number': "switchMultilevel",
    'type-switch': "switchBinary",
    'type-sensor': "sensorMultilevel",
    'type-siren': "siren",
}


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
        if device['permanently_hidden']:
            continue
        prepared_device = {
            **{key: device[key] for key in FIELDS if key in device},
            **{
                key: device["metrics"][key]
                for key in METRICS_SCALE
                if key in device["metrics"]
            },
        }
        prepared_device = set_device_type(prepared_device)
        if prepared_device["deviceType"] == "motor":
            if prepared_device["level"] == "off":
                prepared_device["level"] = 0
            if prepared_device["level"] == "on":
                prepared_device["level"] = 99.0
            prepared_device["level"] = float(prepared_device["level"])

        if "creatorId" in prepared_device and "nodeId" in prepared_device:
            prepared_device[
                "deviceIdentifier"
            ] = f"{prepared_device['creatorId']}_{prepared_device['nodeId']}"
        else:
            prepared_device["deviceIdentifier"] = prepared_device["id"]

        prepared_devices.append(prepared_device)

    return [ZWaveMeData(**d) for d in prepared_devices]


def set_device_type(prepared_device):
    if prepared_device["probeType"] == "siren":
        prepared_device["deviceType"] = "siren"
    if prepared_device["tags"]:
        for tag in prepared_device["tags"]:
            if tag in TYPE_TAGS:
                prepared_device["deviceType"] = TYPE_TAGS[tag]
                prepared_device = set_value_by_device_type(prepared_device)
                return prepared_device
    if prepared_device["probeType"] == "motor":
        prepared_device["deviceType"] = "motor"
    elif prepared_device["probeType"] == "fan":
        prepared_device["deviceType"] = "fan"
    return prepared_device


def set_value_by_device_type(prepared_device) -> dict:
    if prepared_device['deviceType'] == "sensorBinary":
        if prepared_device['level'] in ('on', 'off'):
            return prepared_device
        elif prepared_device['level'] in ('open', 'close'):
            prepared_device['level'] = {'open': 'off', 'close': 'on'}[prepared_device['level']]
        else:
            prepared_device['level'] = 'on' if bool(prepared_device['level']) else 'off'
    elif prepared_device['deviceType'] == 'lightMultilevel':
        if str(prepared_device['level']).replace('.', '', 1).isdigit():
            prepared_device["color"] = {
                "r": round(2.55 * float(prepared_device["level"])),
                "g": round(2.55 * float(prepared_device["level"])),
                "b": round(2.55 * float(prepared_device["level"])),
            }
            prepared_device["level"] = (
                "on" if float(prepared_device["level"]) > 0 else "off"
            )
        elif prepared_device['level'] == 'on':
            prepared_device["color"] = {
                "r": 255,
                "g": 255,
                "b": 255,
            }
        elif prepared_device['level'] == 'off':
            prepared_device["color"] = {
                "r": 0,
                "g": 0,
                "b": 0,
            }
        else:
            prepared_device['level'] = 'on' if bool(prepared_device['level']) else 'off'
            if prepared_device['level'] == 'on':
                prepared_device["color"] = {
                    "r": 255,
                    "g": 255,
                    "b": 255,
                }
            elif prepared_device['level'] == 'off':
                prepared_device["color"] = {
                    "r": 0,
                    "g": 0,
                    "b": 0,
                }
    elif prepared_device['deviceType'] == 'toggleButton':
        return prepared_device
    elif prepared_device['deviceType'] == 'thermostat':
        if str(prepared_device['level']).replace('.', '', 1).isdigit():
            return prepared_device
        elif prepared_device['level'] == 'on':
            prepared_device['level'] = 99
        elif prepared_device['level'] == 'off':
            prepared_device['level'] = 0
        else:
            prepared_device['level'] = 99 if bool(prepared_device['level']) else 0
    elif prepared_device['deviceType'] == 'motor':
        if str(prepared_device['level']).replace('.', '', 1).isdigit():
            return prepared_device
        elif prepared_device['level'] == 'on':
            prepared_device['level'] = 99
        elif prepared_device['level'] == 'off':
            prepared_device['level'] = 0
        else:
            prepared_device['level'] = 99 if bool(prepared_device['level']) else 0
    elif prepared_device['deviceType'] == 'fan':
        if str(prepared_device['level']).replace('.', '', 1).isdigit():
            return prepared_device
        elif prepared_device['level'] == 'on':
            prepared_device['level'] = 99
        elif prepared_device['level'] == 'off':
            prepared_device['level'] = 0
        else:
            prepared_device['level'] = 99 if bool(prepared_device['level']) else 0
    elif prepared_device['deviceType'] == 'doorlock':
        if prepared_device['level'] in ('open', 'close'):
            return prepared_device
        elif prepared_device['level'] in ('on', 'off'):
            prepared_device['level'] = {'off': 'open', 'on': 'close'}[prepared_device['level']]
        else:
            prepared_device['level'] = 'close' if bool(prepared_device['level']) else 'on'

    elif prepared_device['deviceType'] == 'switchMultilevel':
        if str(prepared_device['level']).replace('.', '', 1).isdigit():
            return prepared_device
        elif prepared_device['level'] == 'on':
            prepared_device['level'] = 99
        elif prepared_device['level'] == 'off':
            prepared_device['level'] = 0
        else:
            prepared_device['level'] = 99 if bool(prepared_device['level']) else 0
    elif prepared_device['deviceType'] == 'switchBinary':
        if prepared_device['level'] in ('on', 'off'):
            return prepared_device
        elif prepared_device['level'] in ('open', 'close'):
            prepared_device['level'] = {'open': 'off', 'close': 'on'}[prepared_device['level']]
        else:
            prepared_device['level'] = 'on' if bool(prepared_device['level']) else 'off'
    elif prepared_device['deviceType'] == 'sensorMultilevel':
        if str(prepared_device['level']).replace('.', '', 1).isdigit():
            return prepared_device
        elif prepared_device['level'] == 'on':
            prepared_device['level'] = 99
        elif prepared_device['level'] == 'off':
            prepared_device['level'] = 0
        else:
            prepared_device['level'] = 99 if bool(prepared_device['level']) else 0
    elif prepared_device['deviceType'] == 'siren':
        if prepared_device['level'] in ('on', 'off'):
            return prepared_device
        elif prepared_device['level'] in ('open', 'close'):
            prepared_device['level'] = {'open': 'off', 'close': 'on'}[prepared_device['level']]
        else:
            prepared_device['level'] = 'on' if bool(prepared_device['level']) else 'off'
    return prepared_device
