"""Devices object"""
from typing import List, Dict
from deepmerge import always_merger

from .switch import CoolkitDeviceSwitch


class CoolkitDevice:
    def __init__(self, payload: dict):
        self._payload = payload
        self._switches: List[CoolkitDeviceSwitch] = []
        self._populate_components()

    def get_info(self, param: str):
        if param not in self._payload:
            return None

        return self._payload[param]

    def _populate_components(self):
        if 'switch' in self.params:
            self._switches.append(CoolkitDeviceSwitch(self, 0))
        elif 'switches' in self.params:
            for i in range(0, len(self.params['switches'])):
                self._switches.append(CoolkitDeviceSwitch(self, i))

    @property
    def switches(self):
        return self._switches

    @property
    def params(self) -> dict:
        return self.get_info('params')

    def update_params(self, params: Dict):
        self._payload = always_merger.merge(self._payload, params)

    @property
    def api_key(self) -> str:
        return self.get_info('apikey')

    @property
    def device_id(self) -> str:
        return self.get_info('deviceid')

    @property
    def name(self) -> str:
        return self.get_info('name')

    @property
    def device_type(self) -> str:
        return self.get_info('type')

    @property
    def device_model(self) -> str:
        return self.get_info('extra')['extra']['model']

    @property
    def product_model(self) -> str:
        return self.get_info('productModel')

    @property
    def brand(self) -> str:
        return self.get_info('brandName')

    @property
    def is_online(self) -> bool:
        return self.get_info('online')

    def __repr__(self) -> str:
        return '[' + self.device_id + '] ' + self.brand + ' ' + self.product_model
