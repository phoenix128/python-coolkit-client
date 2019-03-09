"""Component switch"""
from ..log import Log
from ..device_control import CoolkitDeviceControl
from typing import TYPE_CHECKING, Callable, Dict, Awaitable

if TYPE_CHECKING:
    from .device import CoolkitDevice


class CoolkitDeviceSwitch:
    def __init__(self, device: 'CoolkitDevice', index: int):
        self._index = index
        self._device = device
        self._state = False
        self._callbacks: Dict[str, Callable[['CoolkitDeviceSwitch', bool], Awaitable[None]]] = {}

    def get_state(self) -> bool:
        return self._state

    async def update_state(self, new_state: bool) -> None:
        if new_state != self._state:
            self._state = new_state
            for callback in self._callbacks.values():
                await callback(self, new_state)

    def add_state_callback(
            self,
            callback_name: str,
            callable: Callable[['CoolkitDeviceSwitch', bool], Awaitable[None]]
    ) -> None:
        self._callbacks[callback_name] = callable

    def remove_callback(self, callback_name: str) -> None:
        if callback_name in self._callbacks:
            del self._callbacks[callback_name]

    async def set_state(self, state: bool) -> None:
        state_name = 'on' if state else 'off'

        if len(self._device.switches) == 1:
            new_params = {'switch': state_name}
        else:
            new_params = {'switches': self._device.params['switches']}
            new_params['switches'][self._index]['switch'] = state_name

        await CoolkitDeviceControl.update_command(
            device_id=self._device.device_id,
            params=new_params
        )

        await self.update_state(state)
        Log.info('Sent ' + str(self._device) + ' state=' + state_name)
