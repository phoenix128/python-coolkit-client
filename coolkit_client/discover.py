import asyncio
from threading import Thread

from aiohttp import ClientSession

from .devices_repository import CoolkitDevicesRepository
from .device import CoolkitDevice
from .log import Log
from .session import CoolkitSession


class CoolkitDevicesDiscovery:
    @classmethod
    async def discover(cls) -> bool:
        devices_endpoint = CoolkitSession.get_api_endpoint_url('api/user/device')

        async with ClientSession(headers=CoolkitSession.get_auth_headers()) as session:
            async with session.get(devices_endpoint) as response:
                data = await response.json()

                if response.status != 200 or ('error' in data and data['error'] != 0):
                    Log.error('Error while trying to retrieve devices list: ' + str(data['error']))
                    return False

                for device_data in data:
                    if not CoolkitDevicesRepository.has_device(device_data['deviceid']):
                        device = CoolkitDevice(device_data)
                        CoolkitDevicesRepository.add_device(device)
                        Log.info('Registered device: ' + str(device))

        return True

    @classmethod
    async def _discover_in_background(cls) -> None:
        while True:
            await cls.discover()
            await asyncio.sleep(60)

    @classmethod
    def _start_daemon(cls):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(cls._discover_in_background())

    @classmethod
    def start_daemon(cls):
        worker = Thread(target=cls._start_daemon)
        worker.setDaemon(True)
        worker.start()
