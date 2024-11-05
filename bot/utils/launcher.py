import asyncio
import argparse
from itertools import cycle

from pyrogram import Client, compose

from bot.config import settings
from bot.utils import logger
from bot.core.tapper import run_tapper
from bot.core.registrator import register_sessions
from bot.utils.scripts import get_session_names

banner = """


███████╗██╗███████╗     ██████╗ ██████╗ ██████╗ ███████╗██████╗ 
██╔════╝██║╚══███╔╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
███████╗██║  ███╔╝     ██║     ██║   ██║██║  ██║█████╗  ██████╔╝
╚════██║██║ ███╔╝      ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗
███████║██║███████╗    ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║
╚══════╝╚═╝╚══════╝     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝

NotBoredPuppies BOT V 1.0
Prepared and Developed by: F.Davoodi

"""

options = """
Select an action:

    1. Create session
    2. Run clicker
    3. Run via Telegram (Beta)
"""


global tg_clients


async def get_tg_clients() -> list[Client]:
    global tg_clients

    session_names = get_session_names()

    if not session_names:
        raise FileNotFoundError("Not found session files")

    # Membaca query_id dari file query.txt
    try:
        with open('query.txt', 'r') as file:
            query_id = int(file.readline().strip())  # Pastikan query_id adalah integer jika perlu
    except FileNotFoundError:
        raise FileNotFoundError("File 'query.txt' tidak ditemukan. Pastikan file ini ada di direktori yang benar.")
    except ValueError:
        raise ValueError("query_id dalam 'query.txt' tidak valid. Pastikan ini adalah angka.")

    tg_clients = [
        Client(
            name=session_name,
            api_id=query_id,
            workdir="sessions/",
            plugins=dict(root="bot/plugins"),
        )
        for session_name in session_names
    ]

    return tg_clients


async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")

    print(banner)

    logger.info(f"Detected {len(get_session_names())} sessions")

    action = parser.parse_args().action

    if not action:
        print(options)

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Action must be number")
            elif action not in ["1", "2", "3"]:
                logger.warning("Action must be 1, 2 or 3")
            else:
                action = int(action)
                break

    if action == 1:
        await register_sessions()
    elif action == 2:
        tg_clients = await get_tg_clients()
        await run_tasks(tg_clients=tg_clients)
    elif action == 3:
        tg_clients = await get_tg_clients()
        logger.info("Send /help command in Saved Messages\n")
        await compose(tg_clients)


async def run_tasks(tg_clients: list[Client]):
    lock = asyncio.Lock()

    tasks = [
        asyncio.create_task(
            run_tapper(
                tg_client=tg_client,
                lock=lock,
            )
        )
        for tg_client in tg_clients
    ]

    await asyncio.gather(*tasks)
