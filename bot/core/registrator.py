from pyrogram import Client
from bot.utils import logger

async def register_sessions() -> None:
    # Membaca query_id dari file query.txt
    try:
        with open('query.txt', 'r') as file:
            query_id = file.readline().strip()
    except FileNotFoundError:
        raise FileNotFoundError("File 'query.txt' tidak ditemukan. Pastikan file ini ada di direktori yang benar.")

    # Memeriksa apakah query_id tersedia
    if not query_id:
        raise ValueError("query_id tidak ditemukan dalam file 'query.txt'.")

    # Meminta input untuk session_name dari pengguna
    session_name = input('\nEnter the session name (press Enter to exit): ')

    # Menghentikan fungsi jika session_name kosong
    if not session_name:
        print("Session name tidak diberikan. Proses dibatalkan.")
        return None

    # Inisialisasi sesi Client menggunakan query_id tanpa API_ID dan API_HASH
    session = Client(
        name=session_name,
        api_id=int(query_id),  # Pastikan query_id diubah menjadi integer jika diperlukan
        workdir="sessions/"
    )

    # Menjalankan session dan mendapatkan informasi pengguna
    async with session:
        user_data = await session.get_me()

    # Logging hasil sukses
    logger.success(f'Session added successfully @{user_data.username} | {user_data.first_name} {user_data.last_name}')
