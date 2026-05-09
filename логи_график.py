import re
from collections import defaultdict

import pandas as pd
import matplotlib.pyplot as plt

# =========================================
# НАСТРОЙКИ
# =========================================

LOG_FILE = "bot.log"

# =========================================
# РЕГУЛЯРКИ
# =========================================

pattern = re.compile(
    r"(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2},\d+ \| (IN|OUT)"
)

# =========================================
# СБОР СТАТИСТИКИ
# =========================================

stats = defaultdict(lambda: {
    "IN": 0,
    "OUT": 0,
    "ERRORS": 0,
    "USERS": set()
})

with open(LOG_FILE, "r", encoding="utf-8") as f:
    for line in f:

        match = pattern.search(line)

        if not match:
            continue

        date, direction = match.groups()

        # входящие / исходящие
        stats[date][direction] += 1

        # user id
        user_match = re.search(r"\[(\d+)\]", line)

        if user_match:
            stats[date]["USERS"].add(user_match.group(1))

        # ошибки
        lowered = line.lower()

        if (
            "неверный формат" in lowered
            or "неправиль" in lowered
            or "невозможна" in lowered
            or "ошиб" in lowered
        ):
            stats[date]["ERRORS"] += 1

# =========================================
# DATAFRAME
# =========================================

rows = []

for date, data in stats.items():
    rows.append({
        "date": date,
        "Входящие": data["IN"],
        "Исходящие": data["OUT"],
        "Ошибки": data["ERRORS"],
        "Пользователи": len(data["USERS"])
    })

df = pd.DataFrame(rows)

# дата
df["date"] = pd.to_datetime(df["date"])

# сортировка
df = df.sort_values("date")

# =========================================
# ГРУППИРОВКА ПО НЕДЕЛЯМ
# =========================================

df["Неделя"] = df["date"].dt.to_period("W").astype(str)

weekly = (
    df.groupby("Неделя")
    .agg({
        "Входящие": "sum",
        "Исходящие": "sum",
        "Ошибки": "sum",
        "Пользователи": "sum"
    })
    .reset_index()
)

print(weekly)

# =========================================
# ГРАФИК
# =========================================

plt.figure(figsize=(14, 7))

plt.plot(
    weekly["Неделя"],
    weekly["Входящие"],
    marker='o',
    label="Входящие"
)

plt.plot(
    weekly["Неделя"],
    weekly["Исходящие"],
    marker='o',
    label="Исходящие"
)

plt.plot(
    weekly["Неделя"],
    weekly["Ошибки"],
    marker='o',
    label="Ошибки"
)

plt.plot(
    weekly["Неделя"],
    weekly["Пользователи"],
    marker='o',
    label="Пользователи"
)

# оформление
plt.xticks(rotation=45)

plt.title("Статистика бота по неделям")
plt.xlabel("Неделя")
plt.ylabel("Количество")

plt.grid(True)
plt.legend()

plt.tight_layout()

# =========================================
# СОХРАНЕНИЕ
# =========================================

plt.savefig("weekly_stats.png", dpi=300)

# =========================================
# ПОКАЗ
# =========================================

plt.show()