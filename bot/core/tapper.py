import json
import asyncio
from time import time
from random import randint
from urllib.parse import urlparse, parse_qs, unquote

import aiohttp
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestWebView

from bot.config import settings
from bot.utils import logger
from bot.utils.scripts import escape_html
from bot.utils.levels import levels_data, leagues_data
from bot.exceptions import InvalidSession
from .headers import headers


class Tapper:
    def __init__(self, tg_client: Client, lock: asyncio.Lock):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.lock = lock

    async def get_tg_web_data(self) -> str:
        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=await self.tg_client.resolve_peer('NotBoredPuppies_bot'),
                bot=await self.tg_client.resolve_peer('NotBoredPuppies_bot'),
                platform='android',
                from_bot_menu=False,
                url='https://frontend.router9.xyz/'
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {escape_html(error)}")
            await asyncio.sleep(delay=3)

    async def join_telegram(self, data: str) -> bool:
        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)
            
            for dt in data:
                if dt['type'] == 'bot':
                    parsed_url = urlparse(dt['data'])
                    bot_id = parsed_url.path.split('/')[1]
                    query_params = parse_qs(parsed_url.query)
                    ref = query_params.get('start', [None])[0] or query_params.get('startapp', [None])[0]
                    msrf = f"/start {ref}"
                    chat_id = bot_id
                    await self.tg_client.send_message(bot_id, msrf, disable_notification=True)

                if dt['type'] == 'chat':
                    chat_id = dt['data']
                    await self.tg_client.join_chat(dt['data'])

                logger.success(f"{self.session_name} | Successful Joined | "
                                            f"Type: <c>{dt['type']}</c> (<g>{chat_id}</g>)")
                await asyncio.sleep(delay=2)

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return True

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Join Telegram: {escape_html(error)}")
            await asyncio.sleep(delay=3)
            return False

    async def login(self, http_client: aiohttp.ClientSession, tg_web_data: str) -> tuple[dict[str], str]:
        try:
            http_client.headers['Telegram-Data'] = tg_web_data

            response = await http_client.post(url='https://topcoin-backend-prod.router9.live/api/login?platform=android', json={})
            response.raise_for_status()
            access_token = await response.text()

            http_client.headers["App-Token"] = access_token
            response = await http_client.get('https://topcoin-backend-prod.router9.live/api/getUser')
            response.raise_for_status()

            profile_data = await response.json()

            return profile_data, access_token
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while Login: {escape_html(error)} | "
                         f"Response text: {escape_html(response.text)}...")
            await asyncio.sleep(delay=3)

            return {}, ''

    # Other methods remain the same as your original code, but without the proxy

    async def run(self) -> None:
        access_token_created_time = 0
        turbo_time = 0
        active_turbo = False
        turbo_taps = 0

        async with aiohttp.ClientSession(headers=headers) as http_client:
            while True:
                try:
                    if time() - access_token_created_time >= 1800:
                        tg_web_data = await self.get_tg_web_data()
                        profile_data, access_token = await self.login(http_client=http_client, tg_web_data=tg_web_data)

                        if not access_token:
                            continue

                        http_client.headers["App-Token"] = access_token
                        access_token_created_time = time()

                        # Continue processing logic as per your original script...

                    # Additional code for main functionality
                    # without any references to proxy

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {escape_html(error)}")
                    await asyncio.sleep(delay=3)

                else:
                    sleep_between_clicks = randint(a=settings.SLEEP_BETWEEN_TAP[0], b=settings.SLEEP_BETWEEN_TAP[1])
                    logger.info(f"Sleep {sleep_between_clicks}s")
                    await asyncio.sleep(delay=sleep_between_clicks)


async def run_tapper(tg_client: Client, lock: asyncio.Lock):
    try:
        await Tapper(tg_client=tg_client, lock=lock).run()
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
