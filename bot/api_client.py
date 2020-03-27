import asyncio

from aiogram import types
from aiohttp import ClientSession, ClientResponseError


class ApiClientError(Exception):
    pass


class ApiClient:
    def __init__(self, api_url, loop=None):
        self._loop = loop or asyncio.get_event_loop()

        self._session = ClientSession(raise_for_status=True)
        self._api_url = api_url

    async def fetch(
            self,
            method: str = "/",
            verb: str = "POST",
            params: dict = None,
            payload: dict = None,
            headers: dict = None
    ):
        url = self._api_url + method

        try:
            async with self._session.request(
                    verb, url, data=payload, params=params, headers=headers
            ) as response:
                response = await response.json()

            return response
        except ClientResponseError as e:
            raise ApiClientError from e

    async def add_user(self, user: types.User):
        resp = await self.fetch(
            method="/user/add",
            params={
                "user_id": user.id,
                "first_name": user.first_name,
                "username": user.username,
            }
        )
        return resp
