import json
import sys


def load_raw(path):
    text = open(path, encoding="utf-8-sig").read()
    split = text.index("actual")
    forecast_part = text[len("Windfor"):split]
    actual_part = text[split + len("actual"):]
    return json.loads(forecast_part), json.loads(actual_part)


def build(raw_path, out_path):
    forecasts, actuals = load_raw(raw_path)
    seen = set()
    forecast_rows = []
    for row in forecasts:
        key = (row["publishTime"], row["startTime"])
        if key in seen:
            continue
        seen.add(key)
        forecast_rows.append([row["publishTime"], row["startTime"], row["generation"]])
    forecast_rows.sort()
    actual_rows = {}
    for row in actuals:
        if row["fuelType"] == "WIND":
            actual_rows[row["startTime"]] = row["generation"]
    with open(out_path, "w") as f:
        json.dump({"actual": dict(sorted(actual_rows.items())), "forecast": forecast_rows}, f)
    print(len(forecast_rows), len(actual_rows))


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
