import asyncio
from contextlib import suppress
from bot.utils.launcher import process

async def main():
    # Membaca query_id dari file query.txt
    with open('query.txt', 'r') as file:
        query_id = file.readline().strip()
    # Inisialisasi klien Telegram dengan query_id
    client = TelegramClient('session_name', query_id=query_id)
    await client.start()
    await process(client)

if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
