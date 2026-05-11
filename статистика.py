import re
from collections import Counter, defaultdict

def parse_log_file(filepath):
    """
    Анализирует файл логов Telegram-бота.

    Args:
        filepath (str): Путь к файлу лога.

    Returns:
        dict: Словарь со статистикой.
    """

    stats = {
        "total_lines": 0,
        "total_in_messages": 0,
        "total_out_messages": 0,
        "unique_users": set(),
        "unique_bots": set(),
        "error_counts": Counter(),
        "user_message_counts": Counter(),
        "command_counts": Counter(),
        "successful_responses": Counter(),
        "polling_events": 0,
        "failed_polling_events": 0,
        "test_responses_given": 0,
        "expert_requests_made": 0,
        "newsletter_events": 0,
        "other_out_messages": 0,
        "unknown_line_count": 0,
        "raw_data_lines": 0
    }


    in_pattern = re.compile(
        r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3}\s+\|\s+IN\s+\[(?P<user_id>\d+)\]\s+(?P<name>.*?)\s+\(@(?P<username>.*?)\):\s+(?P<text>.*)$"
    )

    out_pattern = re.compile(
        r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3}\s+\|\s+OUT\s+\[(?P<user_id>\d+)\]\s+(?P<name>.*?)\s+\(@(?P<username>.*?)\):\s+(?P<text>.*)$"
    )

    bot_id_pattern = re.compile(r"bot id\s*=\s*(\d+)")

    error_pattern = re.compile(r"Failed to fetch updates - (\w+): (.*)")

    conflict_error_pattern = re.compile(r"Failed to fetch updates - TelegramConflictError: Telegram server says - Conflict: (.*)")

    exception_pattern = re.compile(r"Cause exception while process update")

    not_handled_pattern = re.compile(r"Update id=(\d+) is not handled")
  
    sleep_pattern = re.compile(r"Sleep for ([\d.]+) seconds")

    start_polling_pattern = re.compile(r"Start polling")

    stop_polling_pattern = re.compile(r"Polling stopped for bot")
  
    polling_stopped_pattern = re.compile(r"^Polling stopped$")

    raw_data_pattern = re.compile(r"^[\d\s\.\-\+\/\*]+$")

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            stats["total_lines"] += 1
            line = line.strip()

            if not line:
                continue


            if raw_data_pattern.match(line) or set(line.strip()) <= {'*', '.', ' '}:
                stats["raw_data_lines"] += 1
                continue

            in_match = in_pattern.match(line)
            if in_match:
                stats["total_in_messages"] += 1
                user_id = in_match.group("user_id")
                stats["unique_users"].add(user_id)
                stats["user_message_counts"][user_id] += 1

                text = in_match.group("text")
                if text and text.startswith('/'):
                    command = text.split()[0] 
                    stats["command_counts"][command] += 1
                continue

            out_match = out_pattern.match(line)
            if out_match:
                stats["total_out_messages"] += 1
                user_id = out_match.group("user_id")
                stats["unique_users"].add(user_id) 

                text = out_match.group("text")
                if "контест:" in text:
                    stats["test_responses_given"] += 1
                elif "Сообщение отправлено экспертам" in text:
                    stats["expert_requests_made"] += 1
                elif "Рассылка выполнена для статуса" in text:
                    stats["newsletter_events"] += 1
                else:
                    stats["other_out_messages"] += 1
                continue


            bot_match = bot_id_pattern.search(line)
            if bot_match:
                stats["unique_bots"].add(bot_match.group(1))

            if start_polling_pattern.search(line):
                stats["polling_events"] += 1
                continue
            if stop_polling_pattern.search(line) or polling_stopped_pattern.match(line):
                stats["failed_polling_events"] += 1
                continue


            error_match = error_pattern.search(line)
            if error_match:
                error_type_text = f"{error_match.group(1)}: {error_match.group(2).split(' - ')[0].strip()}"
                stats["error_counts"][error_type_text] += 1
                continue

            conflict_match = conflict_error_pattern.search(line)
            if conflict_match:
                stats["error_counts"]["Conflict: " + conflict_match.group(1)] += 1
                continue

            if exception_pattern.search(line):
                stats["error_counts"]["Exception while processing update"] += 1
                continue

            not_handled_match = not_handled_pattern.search(line)
            if not_handled_match:
                stats["error_counts"]["Update not handled"] += 1
                continue

            if "Ошибка настройки бота" in line:
                stats["error_counts"]["Bot setup error"] += 1
                continue
            if "Неверная команда" in line or "Некорректный ввод" in line or "Ошибка ввода" in line:
                stats["other_out_messages"] += 1 
                continue

            stats["unknown_line_count"] += 1


    stats["unique_users"] = len(stats["unique_users"])
    stats["unique_bots"] = len(stats["unique_bots"])
    stats["error_counts"] = dict(stats["error_counts"])
    stats["user_message_counts"] = dict(stats["user_message_counts"])
    stats["command_counts"] = dict(stats["command_counts"])

    return stats


if __name__ == "__main__":
    log_file = "bot_full.log" 

    print("Запуск анализа логов. Это может занять некоторое время...")
    statistics = parse_log_file(log_file)

    print("\n========== СТАТИСТИКА РАБОТЫ БОТА ==========")
    print(f"Общее количество обработанных строк: {statistics['total_lines']:,}")
    print(f"Количество строк с 'сырыми' данными: {statistics['raw_data_lines']:,}")
    print(f"Нераспознано строк: {statistics['unknown_line_count']:,}")

    print("\n--- Сообщения ---")
    print(f"Входящих сообщений от пользователей: {statistics['total_in_messages']:,}")
    print(f"Исходящих сообщений (ответов бота):   {statistics['total_out_messages']:,}")
    print(f"  - Выдано результатов тестов:        {statistics['test_responses_given']:,}")
    print(f"  - Создано запросов экспертам:        {statistics['expert_requests_made']:,}")
    print(f"  - Выполнено рассылок:                {statistics['newsletter_events']:,}")
    print(f"  - Прочие сообщения (приветствия, ошибки ввода): {statistics['other_out_messages']:,}")

    print("\n--- Пользователи и боты ---")
    print(f"Количество уникальных пользователей: {statistics['unique_users']}")
    print(f"Количество уникальных ботов:         {statistics['unique_bots']}")

    print("\n--- Активность пользователей (топ-5) ---")
    for user_id, count in Counter(statistics['user_message_counts']).most_common(5):
        print(f"  User ID {user_id}: {count} сообщ.")

    print("\n--- Популярные команды (топ-5) ---")
    for command, count in Counter(statistics['command_counts']).most_common(5):
        print(f"  {command}: {count} раз(а)")

    print(f"\n--- События Polling ---")
    print(f"Успешных запусков (Start polling): {statistics['polling_events']}")
    print(f"Аварийных остановок (Polling stopped): {statistics['failed_polling_events']}")

    print(f"\n--- Ошибки ---")
    print(f"Всего различных типов ошибок: {len(statistics['error_counts'])}")
    for error_type, count in Counter(statistics['error_counts']).most_common(10):
        print(f"  [{count:>4}] {error_type}")