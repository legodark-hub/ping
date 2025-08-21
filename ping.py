import asyncio
import sys
import time

import aiohttp


async def ping_host(session: aiohttp.ClientSession, url: str) -> tuple:
    """
    Выполняет одиночный HTTP GET-запрос к указанному URL и измеряет производительность.

    Args:
        session (aiohttp.ClientSession): Сессия aiohttp для выполнения запроса.
        url (str): URL-адрес хоста для пинга.

    Returns:
        tuple: Кортеж, содержащий URL, статус результата ('success', 'failed', 'error')
               и продолжительность запроса в секундах.
    """
    start_time = time.monotonic()
    try:
        async with session.get(url, timeout=10) as response:
            duration = time.monotonic() - start_time
            if response.status < 400:
                return url, "success", duration
            else:
                return url, "failed", duration
    except aiohttp.ClientError as e:
        duration = time.monotonic() - start_time
        print(
            f"[ОШИБКА] Не удалось подключиться к {url}. Причина: {e}", file=sys.stderr
        )
        return url, "error", duration
    except asyncio.TimeoutError:
        duration = time.monotonic() - start_time
        print(f"[ОШИБКА] Запрос к {url} превысил время ожидания.", file=sys.stderr)
        return url, "error", duration
