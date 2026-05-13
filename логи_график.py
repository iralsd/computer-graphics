import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict

LOG_FILE = "bot_full.log"

date_re = re.compile(r"^(\d{4}-\d{2}-\d{2})")
user_re = re.compile(r"\[(\d+)\]")
contest_out_re = re.compile(r"контест:\s*\d+")

IGNORED_USERS = {"398340779", "5278951348"}

stats = defaultdict(lambda: {
    "IN": 0,
    "OUT": 0,
    "TEST_ASKED": 0,
    "TEST_GIVEN": 0,
    "USERS": set()
})

# ================= PARSE =================
all_dates = set()

with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        m = date_re.search(line)
        if not m:
            continue

        date = m.group(1)
        low = line.lower()

        u = user_re.search(line)
        user_id = u.group(1) if u else ""

        if user_id in IGNORED_USERS:
            continue

        if user_id:
            stats[date]["USERS"].add(user_id)
            all_dates.add(pd.Timestamp(date))

        if "| in " in low:
            stats[date]["IN"] += 1
            if "тест на задачу" in low:
                stats[date]["TEST_ASKED"] += 1

        elif "| out " in low:
            stats[date]["OUT"] += 1
            if contest_out_re.search(line):
                stats[date]["TEST_GIVEN"] += 1


# ================= DATA =================
df = pd.DataFrame.from_dict(stats, orient="index")
df.index = pd.to_datetime(df.index)
df = df.sort_index()

df["USERS"] = df["USERS"].apply(len)

# Создаем полный диапазон дат от первой до последней
full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
df_full = pd.DataFrame(index=full_range)
df_full = df_full.join(df)

# Заполняем NaN нулями
df_full["IN"] = df_full["IN"].fillna(0).astype(int)
df_full["OUT"] = df_full["OUT"].fillna(0).astype(int)
df_full["TEST_ASKED"] = df_full["TEST_ASKED"].fillna(0).astype(int)
df_full["TEST_GIVEN"] = df_full["TEST_GIVEN"].fillna(0).astype(int)
df_full["USERS"] = df_full["USERS"].fillna(0).astype(int)

# Группируем по неделям
weekly = df_full.resample("W").sum().reset_index().rename(columns={"index": "date"})

# Добавляем флаг: были ли вообще сообщения на этой неделе
weekly["has_activity"] = (weekly["IN"] + weekly["OUT"]) > 0


# ================= STYLE =================
plt.style.use("seaborn-v0_8-whitegrid")

fig, ax = plt.subplots(figsize=(14, 6))

ax.set_facecolor("#ffffff")
fig.patch.set_facecolor("#ffffff")

ax.grid(True, which="major", linestyle="-", linewidth=0.6, alpha=0.25)
ax.grid(True, which="minor", linestyle=":", linewidth=0.5, alpha=0.15)
ax.minorticks_on()


# ================= PLOT =================
# Основные линии
ax.plot(weekly["date"], weekly["USERS"],
        marker="o", linewidth=2, label="Пользователи", color='#9467bd')
ax.plot(weekly["date"], weekly["IN"],
        linewidth=2, label="Входящие", color='#1f77b4')
ax.plot(weekly["date"], weekly["OUT"],
        linewidth=2, label="Исходящие", color='#ff7f0e')
ax.plot(weekly["date"], weekly["TEST_GIVEN"],
        linestyle="--", linewidth=2, label="Выдано тестов", color='#2ca02c')

# ================= ПЕРИОДЫ ПРОСТОЯ =================
# Находим последовательные недели без активности
inactive_weeks = weekly[~weekly["has_activity"]]

# Группируем последовательные неактивные недели
# if len(inactive_weeks) > 0:
#     inactive_groups = []
#     current_group = []
    
#     for i, row in inactive_weeks.iterrows():
#         if not current_group:
#             current_group.append(row["date"])
#         else:
#             prev_date = current_group[-1]
#             if (row["date"] - prev_date).days <= 7:
#                 current_group.append(row["date"])
#             else:
#                 inactive_groups.append(current_group)
#                 current_group = [row["date"]]
    
#     if current_group:
#         inactive_groups.append(current_group)
    
#     # Добавляем серые зоны для периодов без активности
#     for group in inactive_groups:
#         if len(group) == 1:
#             # Одна неделя — рисуем полосу по центру недели
#             mid = group[0]
#             ax.axvspan(mid - pd.Timedelta(days=3), mid + pd.Timedelta(days=3), 
#                       alpha=0.2, color='gray', label='Нет активности' if group == inactive_groups[0] else "")
#         else:
#             # Несколько недель — рисуем от начала первой до конца последней
#             start = group[0] - pd.Timedelta(days=3)
#             end = group[-1] + pd.Timedelta(days=4)
#             ax.axvspan(start, end, alpha=0.2, color='gray', 
#                       label='Нет активности' if group == inactive_groups[0] else "")

# ================= БЛОКИРОВКА TG =================
# block_start = pd.Timestamp('2026-03-12')
# block_end = weekly["date"].max() + pd.Timedelta(days=4)

# ax.axvspan(block_start, block_end, alpha=0.15, color='red', label='Блокировка TG')
# ax.axvline(x=block_start, color='red', linestyle='--', linewidth=1.5, alpha=0.8)

# ax.text(block_start + pd.Timedelta(days=5), ax.get_ylim()[1] * 0.90, 
#         "Блокировка\nTelegram", fontsize=9, color='red', fontweight='bold',
#         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='red', alpha=0.8))


# ================= AXIS =================
ax.set_title("Активность бота по неделям ", fontsize=14, fontweight="bold", pad=15)
ax.set_ylabel("Количество событий")
ax.set_xlabel("")

ax.legend(loc='upper right', fontsize=9, frameon=True, fancybox=True, shadow=True)

ax.set_xticks(weekly["date"])
ax.set_xticklabels(weekly["date"].dt.strftime("%d.%m"), fontsize=9, rotation=45, ha='right')

ax.grid(alpha=0.3)

ax.set_xlim(weekly["date"].min() - pd.Timedelta(days=3), 
            weekly["date"].max() + pd.Timedelta(days=3))

plt.tight_layout()
plt.savefig("bot_dashboard_with_downtime.png", dpi=300, bbox_inches="tight")
plt.show()

# ================= СТАТИСТИКА ПРОСТОЕВ =================
print("\n===== ПЕРИОДЫ БЕЗ АКТИВНОСТИ =====")
if len(inactive_groups) > 0:
    for i, group in enumerate(inactive_groups, 1):
        start = group[0].strftime('%d.%m.%Y')
        end = group[-1].strftime('%d.%m.%Y')
        days = (group[-1] - group[0]).days + 7
        print(f"{i}. {start} → {end} ({days} дней)")
else:
    print("Нет длительных периодов простоя")

# ================= ОБЩАЯ СТАТИСТИКА =================
active_weeks = weekly[weekly["has_activity"]]
print(f"\n===== ОБЩАЯ СТАТИСТИКА =====")
print(f"Всего недель: {len(weekly)}")
print(f"Активных недель: {len(active_weeks)}")
print(f"Недель без активности: {len(weekly) - len(active_weeks)}")
print(f"Процент активных недель: {len(active_weeks)/len(weekly)*100:.1f}%")