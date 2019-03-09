"""Static class for COOLKIT authoentication"""

import base64
import hashlib
import hmac
import json
import random
import re
import time
import uuid
from aiohttp import ClientSession

from .log import Log
from .const import COOLKIT_APP_ID, COOLKIT_APP_SECRET


class CoolkitSession:
    _bearer_token: str = None
    _user_apikey: str = None
    _region: str = None
    _ws_host: str = None

    @classmethod
    def _get_login_data(cls, username: str, password: str) -> dict:
        """Get application details for auth"""
        login_data = {
            'password': password,
            'version': '6',
            'ts': int(time.time()),
            'nonce': ''.join([str(random.randint(0, 9)) for _ in range(15)]),
            'appid': COOLKIT_APP_ID,
            'imei': str(uuid.uuid4()),
            'os': 'iOS',
            'model': 'iPhone10,6',
            'romVersion': '11.1.2',
            'appVersion': '3.5.3'
        }

        if re.match(r'[^@]+@[^@]+\.[^@]+', username):
            login_data['email'] = username
        else:
            login_data['phoneNumber'] = username

        return login_data

    @classmethod
    def _get_login_headers(cls, login_data: dict) -> dict:
        """Get headers with authorization sign"""
        hex_dig = hmac.new(
            COOLKIT_APP_SECRET,
            str.encode(json.dumps(login_data)),
            digestmod=hashlib.sha256).digest()

        sign = base64.b64encode(hex_dig).decode()

        return {
            'Authorization': 'Sign ' + sign,
            'Content-Type': 'application/json;charset=UTF-8'
        }

    @classmethod
    def get_auth_headers(cls) -> dict:
        """Get authorization headers for subsequent calls"""
        return {
            'Authorization': 'Bearer ' + cls._bearer_token,
            'Content-Type': 'application/json;charset=UTF-8'
        }

    @classmethod
    def get_bearer_token(cls):
        return cls._bearer_token

    @classmethod
    def get_user_api_key(cls):
        return cls._user_apikey

    @classmethod
    def get_ws_endpoint(cls):
        """Get websocket endpoint"""
        return 'wss://{}:8080/api/ws'.format(cls._ws_host)

    @classmethod
    def get_api_endpoint_url(cls, action: str) -> str:
        """Get API URL depending on region"""
        return 'https://{}-api.coolkit.cc:8080/{}'.format(cls._region, action)

    @classmethod
    def get_dispatch_endpoint_url(cls, action: str) -> str:
        """Get dispatch endpoint URL depending on region"""
        return 'https://{}-disp.coolkit.cc:8080/{}'.format(cls._region, action)

    @classmethod
    async def _dispatch_application(cls) -> bool:
        dispatch_url = cls.get_dispatch_endpoint_url('dispatch/app')

        async with ClientSession(headers=cls.get_auth_headers()) as session:
            async with session.post(dispatch_url) as response:
                data = await response.json()

                if response.status != 200 or ('error' in data and data['error'] != 0):
                    Log.error('Error while trying to dispatch application: ' + str(data['error']))
                    return False

                ws_host = data['domain']
                Log.info('Application assigned to ws host ' + ws_host)

                cls._ws_host = ws_host
                return True

    @classmethod
    async def login(cls, username: str, password: str, region: str) -> bool:
        """Login to COOLKIT platform"""
        cls._region = region

        login_url = cls.get_api_endpoint_url('api/user/login')
        login_data = cls._get_login_data(
            username=username,
            password=password
        )
        login_headers = cls._get_login_headers(login_data)

        async with ClientSession(headers=login_headers) as session:
            async with session.post(login_url, json=login_data) as response:
                data = await response.json()

                if response.status != 200 or ('error' in data and data['error'] != 0):
                    Log.error('Error while trying to login: ' + str(data['error']) + ' ' + data['info'])
                    return False

                cls._bearer_token = data['at']
                cls._user_apikey = data['user']['apikey']
                Log.info('User ' + username + ' successfully logged in')

                return await cls._dispatch_application()


