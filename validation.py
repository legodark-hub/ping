import sys
from typing import List
from urllib.parse import urlparse


def validate_count(count: int) -> None:
    """Проверяет, что количество запросов > 0, иначе завершает программу."""
    if count < 1:
        print(
            "[ОШИБКА] Количество запросов (--count) должно быть больше нуля.",
            file=sys.stderr,
        )
        sys.exit(1)


def validate_urls(raw_hosts: List[str]) -> List[str]:
    """
    Проверяет список URL-адресов, возвращая список валидных или завершая программу.
    """
    valid_hosts: List[str] = []
    invalid_hosts: List[str] = []

    for host in raw_hosts:
        if not host:
            continue
        try:
            parsed_url = urlparse(host)
            if parsed_url.scheme and parsed_url.netloc:
                valid_hosts.append(host)
            else:
                invalid_hosts.append(host)
        except ValueError:
            invalid_hosts.append(host)

    if invalid_hosts:
        print(
            f"[ОШИБКА] Обнаружены некорректные или неполные URL: {', '.join(invalid_hosts)}",
            file=sys.stderr,
        )
        print(
            "Пожалуйста, укажите полные URL, включая схему (например, 'https://google.com').",
            file=sys.stderr,
        )
        sys.exit(1)

    if not valid_hosts:
        print(
            "[ОШИБКА] Не найдено ни одного корректного URL для тестирования.",
            file=sys.stderr,
        )
        sys.exit(1)

    return valid_hosts
