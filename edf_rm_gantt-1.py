import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# هر فرایند به صورت (نام، زمان اجرا C، دوره/مهلت T) تعریف می‌شود.
# در این مثال فرض می‌کنیم Deadline = Period و همه فرایندها در زمان صفر آزاد می‌شوند.
TASKS = [
    {"name": "P1", "C": 1, "T": 4},
    {"name": "P2", "C": 2, "T": 5},
    {"name": "P3", "C": 1, "T": 10},
]

def lcm(a, b):
    return a * b // math.gcd(a, b)

def simulate(policy, tasks):
    horizon = math.lcm(*(task["T"] for task in tasks))
    jobs = []
    # ساخت jobهای دوره‌ای تا انتهای افق شبیه‌سازی
    for task in tasks:
        release = 0
        while release < horizon:
            jobs.append({
                "name": task["name"],
                "release": release,
                "deadline": release + task["T"],
                "period": task["T"],
                "remaining": task["C"],
                "burst": task["C"],
                "completion": None,
            })
            release += task["T"]

    timeline = []
    for t in range(horizon):
        ready = [j for j in jobs if j["release"] <= t
                 and j["remaining"] > 0 and j["deadline"] > t]

        if not ready:
            chosen = None
            label = "IDLE"
        elif policy == "EDF":
            # Earliest Deadline First: نزدیک‌ترین deadline اولویت دارد
            chosen = min(ready, key=lambda j: (j["deadline"], j["release"], j["name"]))
            label = chosen["name"]
        elif policy == "RM":
            # Rate Monotonic: دوره کوتاه‌تر، اولویت ثابت بالاتر
            chosen = min(ready, key=lambda j: (j["period"], j["name"], j["release"]))
            label = chosen["name"]
        else:
            raise ValueError("policy must be EDF or RM")

        if chosen is not None:
            chosen["remaining"] -= 1
            if chosen["remaining"] == 0:
                chosen["completion"] = t + 1

        if timeline and timeline[-1][2] == label:
            timeline[-1] = (timeline[-1][0], t + 1, label)
        else:
            timeline.append((t, t + 1, label))

    # آمار jobهایی که deadline آنها داخل افق شبیه‌سازی است
    measured = [j for j in jobs if j["deadline"] <= horizon]
    waits, turnarounds, missed = [], [], 0
    for j in measured:
        if j["completion"] is None:
            missed += 1
        else:
            turnaround = j["completion"] - j["release"]
            waiting = turnaround - j["burst"]
            waits.append(waiting)
            turnarounds.append(turnaround)
            if j["completion"] > j["deadline"]:
                missed += 1

    avg_wait = sum(waits) / len(waits) if waits else 0
    avg_turnaround = sum(turnarounds) / len(turnarounds) if turnarounds else 0
    return timeline, (avg_wait, avg_turnaround, missed), horizon

if __name__ == "__main__":
    results = {}
    for policy in ("EDF", "RM"):
        timeline, stats, horizon = simulate(policy, TASKS)
        results[policy] = stats
        print(f"\\n{policy} Gantt chart (0 to {horizon}):")
        print(" | ".join(f"{start}-{end}:{name}" for start, end, name in timeline))

    print("\\nComparison")
    print(f"{'Algorithm':<12} {'Avg Waiting':>12} {'Avg Turnaround':>16} {'Missed Deadlines':>18}")
    for policy in ("EDF", "RM"):
        waiting, turnaround, missed = results[policy]
        print(f"{policy:<12} {waiting:>12.2f} {turnaround:>16.2f} {missed:>18}")

    # رسم هر دو الگوریتم در یک شکل
    fig, ax = plt.subplots(figsize=(13, 3.8))
    colors = {"P1": "#4C78A8", "P2": "#F58518", "P3": "#54A24B", "IDLE": "#D9D9D9"}
    for row, policy in enumerate(("EDF", "RM")):
        timeline, _, horizon = simulate(policy, TASKS)
        y = 1 - row
        for start, end, name in timeline:
            ax.add_patch(Rectangle((start, y - 0.28), end - start, 0.56,
                                   facecolor=colors[name], edgecolor="white"))
            if end - start >= 1:
                ax.text((start + end) / 2, y, name, ha="center", va="center",
                        fontsize=8, color="black")
        ax.text(-0.4, y, policy, ha="right", va="center", fontweight="bold")
    ax.set_xlim(0, horizon)
    ax.set_ylim(-0.6, 1.6)
    ax.set_xticks(range(0, horizon + 1))
    ax.set_yticks([])
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart Comparison: EDF vs RM (3 periodic processes)")
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    plt.tight_layout()
    plt.savefig("gantt_edf_rm.png", dpi=180, bbox_inches="tight")
    plt.show()
