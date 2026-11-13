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

full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
df_full = pd.DataFrame(index=full_range)
df_full = df_full.join(df)

df_full["IN"] = df_full["IN"].fillna(0).astype(int)
df_full["OUT"] = df_full["OUT"].fillna(0).astype(int)
df_full["TEST_ASKED"] = df_full["TEST_ASKED"].fillna(0).astype(int)
df_full["TEST_GIVEN"] = df_full["TEST_GIVEN"].fillna(0).astype(int)
df_full["USERS"] = df_full["USERS"].fillna(0).astype(int)

weekly = df_full.resample("W").sum().reset_index().rename(columns={"index": "date"})
weekly["has_activity"] = (weekly["IN"] + weekly["OUT"]) > 0


# ================= STYLE =================
plt.style.use("seaborn-v0_8-whitegrid")

fig, ax = plt.subplots(figsize=(10, 7))

ax.set_facecolor("#ffffff")
fig.patch.set_facecolor("#ffffff")

ax.grid(True, which="major", linestyle="-", linewidth=0.6, alpha=0.25, color="black")
ax.grid(True, which="minor", linestyle=":", linewidth=0.5, alpha=0.15, color="black")
ax.minorticks_on()


# ================= PLOT =================
ax.plot(weekly["date"], weekly["USERS"],
        marker="o", markersize=4, linewidth=2,
        label="Пользователи", color="#aaaaaa",
        linestyle="-")

ax.plot(weekly["date"], weekly["IN"],
        linewidth=2, label="Входящие", color="#111111",
        linestyle="-")

ax.plot(weekly["date"], weekly["OUT"],
        linewidth=2, label="Исходящие", color="#555555",
        linestyle=(0, (4, 2)))

ax.plot(weekly["date"], weekly["TEST_GIVEN"],
        linewidth=2, label="Выдано тестов", color="#333333",
        linestyle=(0, (1, 1)))


# ================= AXIS =================
ax.set_title("Активность бота по неделям", fontsize=14, fontweight="bold", pad=15, color="black")
ax.set_ylabel("Количество событий", color="black")
ax.set_xlabel("")

ax.tick_params(colors="black")
for spine in ax.spines.values():
    spine.set_edgecolor("#cccccc")

ax.legend(loc="upper right", fontsize=9, frameon=True, fancybox=False,
          shadow=False, edgecolor="#cccccc")

ax.set_xticks(weekly["date"])
ax.set_xticklabels(weekly["date"].dt.strftime("%d.%m"), fontsize=9, rotation=45, ha="right")

ax.set_xlim(weekly["date"].min() - pd.Timedelta(days=3),
            weekly["date"].max() + pd.Timedelta(days=3))

plt.tight_layout()
plt.savefig("bot_dashboard_bw.png", dpi=300, bbox_inches="tight")
plt.show()


# ================= ОБЩАЯ СТАТИСТИКА =================
active_weeks = weekly[weekly["has_activity"]]
print(f"\n===== ОБЩАЯ СТАТИСТИКА =====")
print(f"Всего недель: {len(weekly)}")
print(f"Активных недель: {len(active_weeks)}")
print(f"Недель без активности: {len(weekly) - len(active_weeks)}")
print(f"Процент активных недель: {len(active_weeks)/len(weekly)*100:.1f}%")


