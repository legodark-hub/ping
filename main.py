import argparse
import asyncio
from collections import defaultdict
import aiohttp
from ping import ping_host
from validation import validate_count, validate_urls


async def main() -> None:
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

    validate_count(args.count)
    raw_hosts = [host.strip() for host in args.hosts.split(",")]
    hosts = validate_urls(raw_hosts)
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
            times = stats[url]["time"]
            times.append(duration)

    for host, data in stats.items():
        print(f"--- Статистика для {host} ---")
        print(f"  Хост:    {host}")
        print(f"  Успешно: {data['success']}")
        print(f"  Неудачно: {data['failed']} (ошибки клиента/сервера)")
        print(f"  Ошибки:  {data['error']} (проблемы с соединением)")

        times = data["time"]
        if isinstance(times, list) and times:
            min_time: float = min(times)
            max_time: float = max(times)
            avg_time: float = sum(times) / len(times)
            print(f"  Мин. время: {min_time:.4f}с")
            print(f"  Макс. время: {max_time:.4f}с")
            print(f"  Сред. время: {avg_time:.4f}с")
        else:
            print("  Нет успешных запросов для расчета статистики по времени.")
        print("-" * (20 + len(host)))


if __name__ == "__main__":
    asyncio.run(main())
