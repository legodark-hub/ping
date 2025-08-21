import argparse
import asyncio
from collections import defaultdict
import aiohttp
from ping import ping_host
from validation import validate_count, validate_urls
import sys


async def main() -> None:
    """
    Основная функция для парсинга аргументов, запуска тестов и отображения статистики.
    """
    parser = argparse.ArgumentParser(
        description="Консольная утилита для тестирования доступности и времени ответа серверов."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-H",
        "--hosts",
        type=str,
        help="Список хостов для тестирования через запятую (например, 'https://ya.ru,https://google.com').",
    )
    group.add_argument(
        "-F",
        "--file",
        type=str,
        help="Путь до файла со списком адресов, разбитых на строки.",
    )
    parser.add_argument(
        "-C",
        "--count",
        type=int,
        default=1,
        help="Количество запросов для каждого хоста. По умолчанию 1.",
    )
    parser.add_argument(
        "-O",
        "--output",
        type=str,
        help="Путь до файла, куда нужно сохранить вывод. Если не указан, то вывод отправляется в консоль.",
    )

    args = parser.parse_args()

    validate_count(args.count)

    if args.hosts:
        raw_hosts = [host.strip() for host in args.hosts.split(",")]
    else:
        try:
            with open(args.file, "r") as f:
                raw_hosts = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[ОШИБКА] Файл не найден: {args.file}")
            sys.exit(1)

    hosts = validate_urls(raw_hosts)
    count = args.count

    output_file = open(args.output, "w") if args.output else None

    def output(message):
        if output_file:
            output_file.write(message + "\n")
        else:
            print(message)

    output(f"Тестируем хосты: {', '.join(hosts)}")
    output(f"Количество запросов для каждого хоста: {count}\n")

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
        output(f"--- Статистика для {host} ---")
        output(f"  Хост:    {host}")
        output(f"  Успешно: {data['success']}")
        output(f"  Неудачно: {data['failed']} (ошибки клиента/сервера)")
        output(f"  Ошибки:  {data['error']} (проблемы с соединением)")

        times = data["time"]
        if isinstance(times, list) and times:
            min_time: float = min(times)
            max_time: float = max(times)
            avg_time: float = sum(times) / len(times)
            output(f"  Мин. время: {min_time:.4f}с")
            output(f"  Макс. время: {max_time:.4f}с")
            output(f"  Сред. время: {avg_time:.4f}с")
        else:
            output("  Нет успешных запросов для расчета статистики по времени.")
        output("-" * (20 + len(host)))


if __name__ == "__main__":
    asyncio.run(main())
