import re
from collections import Counter

# 5151086048 — технический аккаунт тестирования, исключается из total_out
# но его contest/expert/news всё равно учитываются в соответствующих счётчиках
IGNORED_OUT_USERS = {"5151086048"}

# Паттерн выданного теста — только если после "контест:" идёт число
contest_out_re = re.compile(r"контест:\s*\d+")

# Дата отсечки включительно
CUTOFF_DATE = "2026-05-17"


def parse_log_file(filepath):
    stats = {
        "total_lines": 0,
        "total_in_messages": 0,
        "total_out_messages": 0,
        "unique_users": set(),
        "unique_bots": set(),
        "error_counts": Counter(),
        "user_message_counts": Counter(),
        "command_counts": Counter(),
        "polling_events": 0,
        "failed_polling_events": 0,
        "test_requests_asked": 0,
        "test_responses_given": 0,
        "expert_requests_made": 0,
        "newsletter_events": 0,
        "other_out_messages": 0,
        "unknown_line_count": 0,
        "raw_data_lines": 0,
    }

    in_pattern = re.compile(
        r"^(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2},\d{3}\s+\|\s+IN\s+\[(\d+)\].*?:\s+(.*)$"
    )
    out_pattern = re.compile(
        r"^(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2},\d{3}\s+\|\s+OUT\s+\[(\d+)\].*?:\s+(.*)$"
    )
    bot_id_pattern       = re.compile(r"bot id\s*=\s*(\d+)")
    error_pattern        = re.compile(r"Failed to fetch updates - (\w+): (.*)")
    conflict_pattern     = re.compile(r"Failed to fetch updates - TelegramConflictError: Telegram server says - Conflict: (.*)")
    exception_pattern    = re.compile(r"Cause exception while process update")
    not_handled_pattern  = re.compile(r"Update id=(\d+) is not handled")
    start_polling_pattern= re.compile(r"Start polling")
    stop_polling_pattern = re.compile(r"Polling stopped for bot")
    polling_stopped_pat  = re.compile(r"^Polling stopped$")
    raw_data_pattern     = re.compile(r"^[\d\s\.\-\+\/\*]+$")

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            stats["total_lines"] += 1
            line = line.strip()
            if not line:
                continue
            if raw_data_pattern.match(line) or set(line) <= {"*", ".", " "}:
                stats["raw_data_lines"] += 1
                continue

            # ── IN ──────────────────────────────────────────────────────────
            m = in_pattern.match(line)
            if m:
                date, uid, text = m.group(1), m.group(2), m.group(3)
                if date > CUTOFF_DATE:
                    continue
                stats["total_in_messages"] += 1
                stats["unique_users"].add(uid)
                stats["user_message_counts"][uid] += 1
                if text.startswith("/"):
                    stats["command_counts"][text.split()[0]] += 1
                if "тест на задачу" in text.lower():
                    stats["test_requests_asked"] += 1
                continue

            # ── OUT ─────────────────────────────────────────────────────────
            m = out_pattern.match(line)
            if m:
                date, uid, text = m.group(1), m.group(2), m.group(3)
                if date > CUTOFF_DATE:
                    continue
                # contest/expert/news считаются для ВСЕХ пользователей
                if contest_out_re.search(text):
                    stats["test_responses_given"] += 1
                if "Сообщение отправлено экспертам" in text:
                    stats["expert_requests_made"] += 1
                if "Рассылка выполнена для статуса" in text:
                    stats["newsletter_events"] += 1
                # total_out исключает технический аккаунт
                if uid in IGNORED_OUT_USERS:
                    continue
                stats["total_out_messages"] += 1
                stats["unique_users"].add(uid)
                if not (contest_out_re.search(text)
                        or "Сообщение отправлено экспертам" in text
                        or "Рассылка выполнена для статуса" in text):
                    stats["other_out_messages"] += 1
                continue

            # ── системные строки ─────────────────────────────────────────────
            bm = bot_id_pattern.search(line)
            if bm:
                stats["unique_bots"].add(bm.group(1))
            if start_polling_pattern.search(line):
                stats["polling_events"] += 1; continue
            if stop_polling_pattern.search(line) or polling_stopped_pat.match(line):
                stats["failed_polling_events"] += 1; continue
            em = error_pattern.search(line)
            if em:
                stats["error_counts"][f"{em.group(1)}: {em.group(2).split(' - ')[0].strip()}"] += 1; continue
            cm = conflict_pattern.search(line)
            if cm:
                stats["error_counts"]["Conflict: " + cm.group(1)] += 1; continue
            if exception_pattern.search(line):
                stats["error_counts"]["Exception while processing update"] += 1; continue
            nm = not_handled_pattern.search(line)
            if nm:
                stats["error_counts"]["Update not handled"] += 1; continue
            if "Ошибка настройки бота" in line:
                stats["error_counts"]["Bot setup error"] += 1; continue

            stats["unknown_line_count"] += 1

    stats["unique_users"] = len(stats["unique_users"])
    stats["unique_bots"]  = len(stats["unique_bots"])
    stats["error_counts"] = dict(stats["error_counts"])
    stats["user_message_counts"] = dict(stats["user_message_counts"])
    stats["command_counts"] = dict(stats["command_counts"])
    return stats


if __name__ == "__main__":
    log_file = "bot_full.log"
    print("Запуск анализа логов...")
    s = parse_log_file(log_file)

    print(f"\n========== СТАТИСТИКА РАБОТЫ БОТА (до {CUTOFF_DATE}) ==========")
    print(f"Всего обработано строк:        {s['total_lines']:,}")
    print(f"Строк с 'сырыми' данными:      {s['raw_data_lines']:,}")
    print(f"Нераспознано строк:            {s['unknown_line_count']:,}")

    print("\n--- Сообщения ---")
    print(f"Входящих от пользователей:     {s['total_in_messages']:,}")
    print(f"Исходящих ответов бота:        {s['total_out_messages']:,}")
    print(f"  - Запросов на тест (IN):     {s['test_requests_asked']:,}")
    print(f"  - Выдано тестов (OUT):       {s['test_responses_given']:,}")
    print(f"  - Обращений к экспертам:     {s['expert_requests_made']:,}")
    print(f"  - Рассылок выполнено:        {s['newsletter_events']:,}")
    print(f"  - Прочие исходящие:          {s['other_out_messages']:,}")

    print("\n--- Пользователи ---")
    print(f"Уникальных пользователей:      {s['unique_users']}")
    print(f"Уникальных ботов:              {s['unique_bots']}")

    print("\n--- Топ-5 активных пользователей ---")
    for uid, cnt in Counter(s["user_message_counts"]).most_common(5):
        print(f"  User ID {uid}: {cnt} сообщ.")

    print("\n--- Топ-5 команд ---")
    for cmd, cnt in Counter(s["command_counts"]).most_common(5):
        print(f"  {cmd}: {cnt} раз(а)")

    print("\n--- Polling ---")
    print(f"Успешных запусков:             {s['polling_events']}")
    print(f"Аварийных остановок:           {s['failed_polling_events']}")

    print(f"\n--- Ошибки ({len(s['error_counts'])} типов) ---")
    for err, cnt in Counter(s["error_counts"]).most_common(10):
        print(f"  [{cnt:>4}] {err}")