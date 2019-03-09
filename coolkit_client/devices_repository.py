"""Devices repository"""
from typing import Dict, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .device import CoolkitDevice


class CoolkitDevicesRepository:
    _devices: Dict[str, 'CoolkitDevice'] = {}

    @classmethod
    def get_devices(cls) -> Dict[str, 'CoolkitDevice']:
        return cls._devices

    @classmethod
    def has_device(cls, device_id: str) -> bool:
        return device_id in cls._devices

    @classmethod
    def get_device(cls, device_id: str) -> Optional['CoolkitDevice']:
        if device_id not in cls._devices:
            return None

        return cls._devices[device_id]

    @classmethod
    def add_device(cls, device: 'CoolkitDevice') -> None:
        cls._devices[device.device_id] = device
