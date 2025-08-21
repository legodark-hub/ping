import argparse
import asyncio
import time
from collections import defaultdict
import aiohttp


async def ping_host(session, url):
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
        print(f"[ОШИБКА] Не удалось подключиться к {url}. Причина: {e}")
        return url, "error", duration
    except asyncio.TimeoutError:
        duration = time.monotonic() - start_time
        print(f"[ОШИБКА] Запрос к {url} превысил время ожидания.")
        return url, "error", duration


async def main():
    """
    Основная функция для парсинга аргументов, запуска тестов и отображения статистики.
    """
    parser = argparse.ArgumentParser(
        description="Консольная утилита для тестирования доступности и времени ответа серверов."
    )
    parser.add_argument(
        "-H",
        "--hosts",
        required=True,
        type=str,
        help="Список хостов для тестирования через запятую (например, 'https://ya.ru,https://google.com').",
    )
    parser.add_argument(
        "-C",
        "--count",
        type=int,
        default=1,
        help="Количество запросов для каждого хоста. По умолчанию 1.",
    )

    args = parser.parse_args()
    hosts = [host.strip() for host in args.hosts.split(",")]
    count = args.count

    print(f"Тестируем хосты: {', '.join(hosts)}")
    print(f"Количество запросов для каждого хоста: {count}\n")

    tasks = []
    async with aiohttp.ClientSession() as session:
        for host in hosts:
            for _ in range(count):
                tasks.append(ping_host(session, host))

        results = await asyncio.gather(*tasks)

    stats = defaultdict(lambda: {"success": 0, "failed": 0, "error": 0, "time": []})

    for url, status, duration in results:
        stats[url][status] += 1
        if status == "success":
            stats[url]["time"].append(duration)

    for host, data in stats.items():
        print(f"--- Статистика для {host} ---")
        print(f"  Хост:    {host}")
        print(f"  Успешно: {data['success']}")
        print(f"  Неудачно: {data['failed']} (ошибки клиента/сервера)")
        print(f"  Ошибки:  {data['error']} (проблемы с соединением)")

        if data["time"]:
            min_time = min(data["time"])
            max_time = max(data["time"])
            avg_time = sum(data["time"]) / len(data["time"])
            print(f"  Мин. время: {min_time:.4f}с")
            print(f"  Макс. время: {max_time:.4f}с")
            print(f"  Сред. время: {avg_time:.4f}с")
        else:
            print("  Нет успешных запросов для расчета статистики по времени.")
        print("-" * (20 + len(host)))


if __name__ == "__main__":
    asyncio.run(main())
