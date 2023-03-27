from datetime import date, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

df: pd.DataFrame = pd.read_csv("./dwd_tasks.csv")

COLOR_DICT = {"TODO": "#E64646", "STRT": "#E69646", "DONE": "#34D05C"}


def color(row):
    return COLOR_DICT[row["STATUS"]]


df = (
    df
    .astype({"STATUS": "category"})
    .assign(schedule_date=pd.to_datetime(df.START, format="[%Y-%m-%d %a]"))
    .assign(deadline_date=pd.to_datetime(df.DEADLINE, format="[%Y-%m-%d %a]"))
    .assign(start_num=lambda df_: (df_.schedule_date - df_.schedule_date.min()).dt.days)
    .assign(end_num=lambda df_: (df_.deadline_date - df_.schedule_date.min()).dt.days)
    .assign(duration=lambda df_: df_.end_num - df_.start_num)
    .assign(color=df.apply(color, axis=1))
    .sort_values("schedule_date", ascending=False)
)

# plot
fig, ax = plt.subplots(1, figsize=(10, 6))
ax.barh(df.TASK, df.duration, left=df.start_num, color=df.color)

# grid lines
ax.set_axisbelow(True)
ax.xaxis.grid(color="k", linestyle="dashed", alpha=0.1, which="both")

# tickmarks
xticks = np.arange(-4, df.end_num.max() + 1, 7)
xticks_labels = pd.date_range(
    df.schedule_date.min() - timedelta(4), end=df.deadline_date.max()
).strftime("%m/%d")
xticks_minor = np.arange(-4, df.end_num.max() + 1, 1)

ax.set_xticks(xticks)
# ax.set_xticks(xticks_minor, minor=True)
ax.set_xticklabels(xticks_labels[::7])
ax.set_yticklabels(df.TASK)
ax.tick_params(left=False, bottom=False)

plt.setp([ax.get_xticklines()], color="w")


# align x axis
ax.set_xlim(-4, df.end_num.max())

# remove spines
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["left"].set_position(("outward", 10))
ax.spines["top"].set_visible(False)
ax.spines["bottom"].set_color("w")

# title
ax.set_title("Lunch Detention 2023")

# legend
legend_elements = [Patch(facecolor=COLOR_DICT[i], label=i) for i in COLOR_DICT]
plt.legend(handles=legend_elements)

# Get "Today" value from sys date/ date.today()
today = pd.Timestamp(date.today())
today = today - df.schedule_date.min()
# plot line for today
ax.axvline(today.days, color="k", lw=1, alpha=0.7)
ax.text(today.days, len(df) + 0.5, "Today", ha="right", color="k")

plt.tight_layout()
plt.savefig("gantt_chart.png")
plt.show()
