import asyncio
import json
import threading
import time

from .helpers import prepare_devices
from .WebsocketListener import WebsocketListener


class ZWaveMe:
    """Main controller class"""

    def __init__(
        self,
        url,
        token=None,
        on_device_create=None,
        on_device_update=None,
        on_device_remove=None,
        on_device_destroy=None,
        on_new_device=None,
        platforms=None,
    ):
        self.on_device_create = on_device_create
        self.on_device_update = on_device_update
        self.on_device_remove = on_device_remove
        self.on_device_destroy = on_device_destroy
        self.on_new_device = on_new_device
        self.url = url
        self.token = token
        self.platforms = platforms
        self._ws = None
        self._wshost = None
        self.thread = None
        self.devices = []
        self.uuid = None
        self.is_closed = False

    def start_ws(self):
        """Launch thread."""
        self.thread = threading.Thread(target=self.init_websocket)
        self.thread.daemon = True
        self.thread.start()

    async def get_connection(self):
        """verify connection"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.start_ws)

        try:
            await asyncio.wait_for(self._ws.connect(), timeout=10.0)
            return True

        except asyncio.TimeoutError:
            await self.close_ws()
            return False

    async def wait_for_info(self):
        while not self.uuid:
            await asyncio.sleep(0.1)
        return self.uuid

    async def close_ws(self):
        loop = asyncio.get_event_loop()
        self.is_closed = True
        blocking_tasks = [
            loop.run_in_executor(None, self.thread.join),
            loop.run_in_executor(None, self._ws.close),
        ]
        await asyncio.wait(blocking_tasks)

    async def get_uuid(self):
        """Get uuid info"""
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.get_info)
        try:
            await asyncio.wait_for(self.wait_for_info(), timeout=5.0)
            return self.uuid
        except asyncio.TimeoutError:
            return

    def send_command(self, device_id, command):
        self._ws.send(
            json.dumps(
                {
                    "event": "httpEncapsulatedRequest",
                    "data": {
                        "method": "GET",
                        "url": "/ZAutomation/api/v1/devices/{}/command/{}".format(
                            device_id, command
                        ),
                    },
                }
            )
        )

    def get_devices(self):
        self._ws.send(
            json.dumps(
                {
                    "event": "httpEncapsulatedRequest",
                    "responseEvent": "get_devices",
                    "data": {"method": "GET", "url": "/ZAutomation/api/v1/devices"},
                }
            )
        )

    def get_device_info(self, device_id):
        self._ws.send(
            json.dumps(
                {
                    "event": "httpEncapsulatedRequest",
                    "responseEvent": "get_device_info",
                    "data": {
                        "method": "GET",
                        "url": "/ZAutomation/api/v1/devices/{}".format(device_id),
                    },
                }
            )
        )

    def get_info(self):
        self._ws.send(
            json.dumps(
                {
                    "event": "httpEncapsulatedRequest",
                    "responseEvent": "get_info",
                    "data": {
                        "method": "GET",
                        "url": "/ZAutomation/api/v1/system/first-access",
                    },
                }
            )
        )

    def init_websocket(self):
        # keep websocket open indefinitely
        while True:
            if self.is_closed:
                return
            self._ws = WebsocketListener(
                ZWaveMe=self,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                token=self.token,
                url=self.url,
            )

            try:
                self._ws.run_forever(ping_interval=5)
            finally:
                self._ws.close()
            time.sleep(5)

    def on_message(self, _, utf):
        if utf:
            dict_data = json.loads(utf)
            if "type" not in dict_data.keys():
                return
            try:
                if dict_data["type"] == "get_devices":
                    if "data" not in dict_data or "body" not in dict_data["data"]:
                        return

                    body = json.loads(dict_data["data"]["body"])
                    if "devices" in body["data"]:
                        self.devices = prepare_devices([
                            device
                            for device in body["data"]["devices"]
                            if device["deviceType"] in self.platforms
                        ])
                        if self.on_device_create:
                            self.on_device_create(self.devices)

                elif dict_data["type"] == "get_device_info":
                    if "data" not in dict_data or "body" not in dict_data["data"]:
                        return
                    body = json.loads(dict_data["data"]["body"])
                    if "id" in body["data"]:
                        new_device = prepare_devices(
                            [
                                body["data"],
                            ]
                        )[0]
                        if self.on_new_device:
                            self.on_new_device(new_device)

                elif dict_data["type"] == "me.z-wave.devices.level":
                    device = prepare_devices(
                        [
                            dict_data["data"],
                        ]
                    )[0]
                    if device.deviceType == "sensorMultilevel":
                        device.level = str(
                            round(float(dict_data["data"]["metrics"]["level"]), 1)
                        )
                    if self.on_device_update:
                        self.on_device_update(device)

                elif dict_data["type"] == "me.z-wave.namespaces.update":
                    for data in dict_data["data"]:
                        if data["id"] == "devices_all":
                            new_devices = [x["deviceId"] for x in data["params"]]
                            devices_to_install = set(new_devices) - set(
                                [x["id"] for x in self.devices]
                            )
                            for device in devices_to_install:
                                self.get_device_info(device)

                elif dict_data["type"] == "get_info":
                    uuid = json.loads(dict_data["data"]["body"])["data"]["uuid"]
                    if uuid and uuid is not None:
                        self.uuid = uuid

                elif dict_data["type"] == "me.z-wave.devices.remove":
                    if self.on_device_remove:
                        self.on_device_remove(dict_data["data"])

                elif dict_data["type"] == "me.z-wave.devices.wipe":
                    if self.on_device_destroy:
                        self.on_device_destroy(dict_data["data"])

            except Exception as e:
                pass

    def on_error(self, *args, **kwargs):
        error = args[-1]

    def on_close(self, _, *args):
        self._ws.connected = False

    def get_ws(self):
        return self._ws

    def get_wshost(self):
        return self._wshost
