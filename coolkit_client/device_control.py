"""Devices control"""
import asyncio
import json
import random
import time
import websockets
from asyncio import AbstractEventLoop
from .devices_repository import CoolkitDevicesRepository
from .log import Log
from .session import CoolkitSession


class CoolkitDeviceControl:
    _websocket: websockets.WebSocketClientProtocol = None
    _ready = False

    @classmethod
    def _get_auth_payload(cls) -> dict:
        return {
            'action': "userOnline",
            'userAgent': 'app',
            'version': 6,
            'nonce': ''.join([str(random.randint(0, 9)) for _ in range(15)]),
            'apkVesrion': "1.8",
            'os': 'ios',
            'at': CoolkitSession.get_bearer_token(),
            'apikey': CoolkitSession.get_user_api_key(),
            'ts': str(int(time.time())),
            'model': 'iPhone10,6',
            'romVersion': '11.1.2',
            'sequence': str(time.time()).replace('.', '')
        }

    @classmethod
    async def disconnect(cls) -> None:
        await cls._websocket.close()
        cls._websocket = None

    @classmethod
    async def connect(cls) -> bool:
        """Connect websocket for real time updates"""
        if cls._websocket is None:
            ws_endpoint = CoolkitSession.get_ws_endpoint()

            cls._websocket = await websockets.connect(ws_endpoint)
            await cls._ws_send(cls._get_auth_payload())

            data = await cls._ws_read()
            if 'error' in data and data['error'] != 0:
                Log.error('Error while trying to connect websocket: ' + str(data['error']))
                await cls.disconnect()
                return False

            Log.info('Websocket successfully connected')

        cls._ready = True
        return True

    @classmethod
    async def _ws_read(cls) -> dict:
        await cls.connect()
        return json.loads(await cls._websocket.recv())

    @classmethod
    async def _ws_send(cls, payload: dict) -> None:
        await cls.connect()
        await cls._websocket.send(json.dumps(payload))

    @classmethod
    async def _listen_ws(cls):
        loop = asyncio.get_event_loop()

        await cls.connect()
        while True:
            data = await cls._ws_read()
            if data is not None:
                if 'deviceid' in data and 'params' in data:
                    device_id = data.get('deviceid')
                    CoolkitDevicesRepository.get_device(device_id).update_params(data['params'])

                if data.get('action') == 'update':
                    if data['params'].get('switch'):
                        await loop.create_task(cls._on_update_switch(data, loop))
                    elif data['params'].get('switches'):
                        await loop.create_task(cls._on_update_switches(data, loop))

    @classmethod
    async def _on_update_switch(cls, data: dict, loop: AbstractEventLoop) -> None:
        """Update device with a single outlet"""
        device = CoolkitDevicesRepository.get_device(data['deviceid'])
        if device is None:
            return

        await loop.create_task(device.switches[0].update_state(data['params']['switch'] == 'on'))

    @classmethod
    async def _on_update_switches(cls, data: dict, loop: AbstractEventLoop) -> None:
        """Update device with multiple outlets"""
        device = CoolkitDevicesRepository.get_device(data['deviceid'])
        if device is None:
            return

        for switch in data['params']['switches']:
            index = int(switch['outlet'])
            await loop.create_task(device.switches[index].update_state(switch['switch'] == 'on'))

    @classmethod
    def start_daemon(cls):
        loop = asyncio.get_event_loop()
        loop.create_task(cls._listen_ws())

    @classmethod
    async def update_command(
        cls,
        params: dict,
        device_id: str
    ) -> None:
        if not cls._ready:
            return

        device = CoolkitDevicesRepository.get_device(device_id)

        payload = {
            'action': 'update',
            'userAgent': 'app',
            'params': params,
            'apikey': device.api_key,
            'deviceid': device.device_id,
            'sequence': str(time.time()).replace('.', ''),
            'controlType': device.params['controlType'] if 'controlType' in device.params else 4,
            'ts': 0
        }

        if device.api_key != CoolkitSession.get_user_api_key():
            payload['selfApikey'] = CoolkitSession.get_user_api_key()

        await cls._ws_send(payload)
