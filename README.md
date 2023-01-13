ZWave-Me-WS is a websocket connection library for [Z-Wave.Me Z-Way](https://z-wave.me/z-way/) controllers

**Installing**

To install this package use:

`pip install zwave-me-ws`

**Usage**

To use the connector initialize the API using:

```
from zwave_me_ws import ZWaveMe, ZWaveMeData

zwave_api = ZWaveMe(
  on_device_create=on_device_func
  on_device_update=on_device_update_func,
  on_new_device=on_device_add_func,
  token="....", # Z-Way access token in the form .../... (remote) of /... (local)
  url="...", # wss://find.z-wave.me or ws://IP:8083
  platforms=[...]
)

def on_device_add_func(self, device: ZWaveMeData)

def on_device_create_func(self, devices: list[ZWaveMeData])

def on_device_update_func(self, new_info: ZWaveMeData)
```

Here `platforms` is the list of deviceType fields to handle. Used to filter only types supported by your application. For example, 
`["sensorBinary", "lightMultilevel", "toggleButton", "thermostat", "motor", "fan", "doorlock", "switchMultilevel", "switchBinary", "sensorMultilevel", "siren", "switchRGBW", "switchRGB"]`.

Available functions:
```
devices = zwave_api.get_devices()

zwave_api.send_command(device_id, command) # command can be "on", "off", "exact?level=..", "open", "close"

is_connected = zwave_api.get_connection()

zwave_api.close_ws()
```

Device (ZWaveMeData) has the following fields:
```
  id: str
  deviceType: str
  title: str
  level: Union[str, int, float]
  deviceIdentifier: str
  probeType: str
  scaleTitle: str
  min: str
  max: str
  color: dict
  isFailed: bool
  locationName: str
  manufacturer: str
  firmware: str
  tags: list[str]
  nodeId: str
  creatorId: str
```
