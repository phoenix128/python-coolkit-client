# ewelink-sonoff-coolkit-client
Client for Sonoff devices using eWeLink access

Inspired by https://github.com/peterbuga/HASS-sonoff-ewelink

## Usage example
```
#!/usr/bin/env python
import asyncio

from coolkit_client import CoolkitSession, CoolkitDevicesRepository
from coolkit_client.device_control import CoolkitDeviceControl
from coolkit_client.discover import CoolkitDevicesDiscovery


async def start():
    await CoolkitSession.login(
        username='my@email.com',
        password='IDoNotTellYou!',
        region='eu'
    )

    await CoolkitDevicesRepository.get_device('1000012345').switches[0].state(True)
    await asyncio.sleep(1)
    await CoolkitDevicesRepository.get_device('1000012345').switches[0].state(False)

    await CoolkitDevicesDiscovery.discover()
    CoolkitDeviceControl.start_daemon()

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())

```
