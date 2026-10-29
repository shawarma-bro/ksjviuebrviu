import os

from flask import Flask, jsonify, request, send_from_directory

from . import analysis

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

app = Flask(__name__, static_folder=None)


def read_cutoff():
    try:
        value = int(request.args.get("cutoff", 9))
    except ValueError:
        value = 9
    return min(max(value, 0), 23)


@app.route("/api/meta")
def meta():
    days = analysis.delivery_dates()
    return jsonify({"days": days, "default_cutoff": 9})


@app.route("/api/day")
def day():
    days = analysis.delivery_dates()
    selected = request.args.get("date", days[0])
    if selected not in days:
        return jsonify({"error": "date out of range"}), 400
    return jsonify(analysis.day_view(selected, read_cutoff()))


@app.route("/api/metrics")
def metrics():
    return jsonify(analysis.metrics(read_cutoff()))


@app.route("/api/horizon")
def horizon():
    return jsonify(analysis.horizon_view())


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def frontend(path):
    full = os.path.join(STATIC_DIR, path)
    if path and os.path.isfile(full):
        return send_from_directory(STATIC_DIR, path)
    return send_from_directory(STATIC_DIR, "index.html")
