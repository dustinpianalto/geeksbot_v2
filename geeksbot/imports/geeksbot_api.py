import aiohttp
import asyncio
import logging

logger = logging.getLogger("Geeksbot API")


class APIError500(Exception):
    pass


class APIError(Exception):
    pass


class GeeksbotAPI:
    def __init__(
        self,
        token: str,
        base_url: str = "https://geeksbot.app/api",
        loop: asyncio.AbstractEventLoop = None,
    ):
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.base_url = base_url
        self.token = token
        self.auth_header = {"Authorization": f"Token {self.token}"}

    def clean_endpoint(endpoint: str) -> str:
        endpoint = endpoint[1:] if endpoint.startswith("/") else endpoint
        endpoint += "/" if not endpoint.endswith("/") else ""
        return endpoint

    async def query(
        self, method: str, endpoint: str, data: dict = None, query: dict = None
    ):
        endpoint = self.clean_endpoint(endpoint)
        if method.lower() == "get":
            resp = await self.session.get(
                f"{self.base_url}/{endpoint}{query_str}",
                headers=self.auth_header,
                params=query,
                json=data,
            )
        elif method.lower() == "post":
            resp = await self.session.post(
                f"{self.base_url}/{endpoint}{query_str}",
                headers=self.auth_header,
                params=query,
                json=data,
            )
        elif method.lower() == "put":
            resp = await self.session.put(
                f"{self.base_url}/{endpoint}{query_str}",
                headers=self.auth_header,
                params=query,
                json=data,
            )
        elif method.lower() == "delete":
            resp = await self.session.delete(
                f"{self.base_url}/{endpoint}{query_str}",
                headers=self.auth_header,
                params=query,
                json=data,
            )
        else:
            raise APIError(f"That is not a valid method. {method}")

        if resp.status == 200:
            return await resp.json()
        elif resp.status >= 500:
            raise APIError500(
                "The server returned a 500 error. "
                "The developers have been notified of the issue."
            )
        else:
            details = (await resp.json())["details"]
            raise APIError(details)
