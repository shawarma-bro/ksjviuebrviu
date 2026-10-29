import json
import math
import os
from bisect import bisect_right
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from functools import lru_cache

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "wind.json")
FIRST_DELIVERY = "2026-01-02"
LAST_DELIVERY = "2026-01-31"


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def fmt(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@lru_cache(maxsize=1)
def load():
    with open(DATA_PATH) as f:
        raw = json.load(f)
    halves = defaultdict(list)
    for start, value in raw["actual"].items():
        dt = parse(start)
        halves[dt.replace(minute=0)].append(value)
    actual = {hour: sum(v) / len(v) for hour, v in halves.items()}
    versions = defaultdict(list)
    for publish, start, value in raw["forecast"]:
        versions[parse(start)].append((parse(publish), value))
    for key in versions:
        versions[key].sort()
    return actual, versions


def delivery_dates():
    start = datetime.fromisoformat(FIRST_DELIVERY)
    end = datetime.fromisoformat(LAST_DELIVERY)
    days = []
    while start <= end:
        days.append(start.strftime("%Y-%m-%d"))
        start += timedelta(days=1)
    return days


def pick_forecast(target, cutoff):
    _, versions = load()
    options = versions.get(target, [])
    times = [p for p, _ in options]
    idx = bisect_right(times, cutoff)
    if idx == 0:
        return None
    return options[idx - 1]


def cutoff_for(day, cutoff_hour):
    d = datetime.fromisoformat(day).replace(tzinfo=timezone.utc)
    return d - timedelta(days=1) + timedelta(hours=cutoff_hour)


@lru_cache(maxsize=32)
def decision_rows(cutoff_hour):
    actual, _ = load()
    rows = []
    for day in delivery_dates():
        cutoff = cutoff_for(day, cutoff_hour)
        base = datetime.fromisoformat(day).replace(tzinfo=timezone.utc)
        for h in range(24):
            target = base + timedelta(hours=h)
            if target not in actual:
                continue
            chosen = pick_forecast(target, cutoff)
            if chosen is None:
                continue
            publish, value = chosen
            rows.append({
                "time": fmt(target),
                "day": day,
                "hour": h,
                "forecast": value,
                "actual": round(actual[target], 1),
                "error": round(value - actual[target], 1),
                "publish": fmt(publish),
            })
    return rows


def quantile(sorted_values, q):
    if not sorted_values:
        return 0.0
    pos = (len(sorted_values) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)


def summarize(rows):
    n = len(rows)
    if n == 0:
        return {"n": 0}
    errors = [r["error"] for r in rows]
    abs_errors = sorted(abs(e) for e in errors)
    signed = sorted(errors)
    mean_actual = sum(r["actual"] for r in rows) / n
    mae = sum(abs_errors) / n
    return {
        "n": n,
        "mae": round(mae, 1),
        "rmse": round(math.sqrt(sum(e * e for e in errors) / n), 1),
        "bias": round(sum(errors) / n, 1),
        "mape": round(100 * sum(abs(r["error"]) / r["actual"] for r in rows if r["actual"] > 0) / n, 1),
        "nmae": round(100 * mae / mean_actual, 1),
        "mean_actual": round(mean_actual, 1),
        "p50": round(quantile(abs_errors, 0.5), 1),
        "p90": round(quantile(abs_errors, 0.9), 1),
        "p95": round(quantile(abs_errors, 0.95), 1),
        "shortfall_p90": round(quantile(signed, 0.9), 1),
        "surplus_p90": round(quantile(signed, 0.1), 1),
    }


def metrics(cutoff_hour):
    rows = decision_rows(cutoff_hour)
    by_hour = []
    for h in range(24):
        subset = [r for r in rows if r["hour"] == h]
        s = summarize(subset)
        by_hour.append({"hour": h, "mae": s.get("mae", 0), "bias": s.get("bias", 0)})
    by_day = []
    for day in delivery_dates():
        subset = [r for r in rows if r["day"] == day]
        s = summarize(subset)
        by_day.append({"day": day, "mae": s.get("mae", 0), "bias": s.get("bias", 0)})
    return {"summary": summarize(rows), "by_hour": by_hour, "by_day": by_day}


def day_view(day, cutoff_hour):
    rows = [r for r in decision_rows(cutoff_hour) if r["day"] == day]
    overall = summarize(decision_rows(cutoff_hour))
    for r in rows:
        r["safe_wind"] = round(max(r["forecast"] - overall["shortfall_p90"], 0), 1)
        r["high_wind"] = round(r["forecast"] - overall["surplus_p90"], 1)
    publishes = sorted({r["publish"] for r in rows})
    return {
        "day": day,
        "cutoff": fmt(cutoff_for(day, cutoff_hour)),
        "publish_times": publishes,
        "rows": rows,
        "summary": summarize(rows),
    }


def horizon_view(bucket=6, max_hours=48):
    actual, versions = load()
    buckets = defaultdict(list)
    for target, options in versions.items():
        if target not in actual:
            continue
        if not (FIRST_DELIVERY <= target.strftime("%Y-%m-%d") <= LAST_DELIVERY):
            continue
        for publish, value in options:
            horizon = (target - publish).total_seconds() / 3600
            if horizon < 0 or horizon >= max_hours:
                continue
            buckets[int(horizon // bucket)].append(abs(value - actual[target]))
    out = []
    for key in sorted(buckets):
        values = buckets[key]
        out.append({
            "label": f"{key * bucket}-{(key + 1) * bucket}h",
            "mae": round(sum(values) / len(values), 1),
            "n": len(values),
        })
    return out
