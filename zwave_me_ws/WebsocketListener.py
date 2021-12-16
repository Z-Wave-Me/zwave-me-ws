import asyncio
import json
import threading
import time

import websocket


class WebsocketListener(threading.Thread, websocket.WebSocketApp):
    def __init__(
        self,
        ZWaveMe,
        on_message=None,
        on_error=None,
        on_close=None,
        token=None,
        url=None,
    ):
        self._ZWaveMe = ZWaveMe

        threading.Thread.__init__(self)
        websocket.WebSocketApp.__init__(
            self,
            url,
            header={"Authorization": "Bearer " + token},
            on_open=self.on_open,
            on_error=on_error,
            on_message=on_message,
            on_close=on_close,
        )

        self.connected = False
        self.last_update = time.time()

    async def connect(self):
        while not self.connected:
            await asyncio.sleep(0.1)
        return self.connected

    def on_open(self, *args):
        self.connected = True
        self.last_update = time.time()

        self.send(
            json.dumps(
                {
                    "event": "httpEncapsulatedRequest",
                    "responseEvent": "get_devices",
                    "data": {"method": "GET", "url": "/ZAutomation/api/v1/devices"}
                }
            )
        )

    def run_forever(
        self, sockopt=None, sslopt=None, ping_interval=0, ping_timeout=None, **kwargs):
        websocket.WebSocketApp.run_forever(
            self,
            sockopt=sockopt,
            sslopt=sslopt,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
            **kwargs
        )
