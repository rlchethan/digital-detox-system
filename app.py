import os
import secrets
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for

import database as db

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(16))
db.init_db()


def _dashboard_context():
    goal = db.get_daily_goal_minutes()
    today = db.today_total_minutes()
    weekly = db.weekly_app_totals()
    week_max = max((r["total"] for r in weekly), default=1)
    usage = db.list_recent_usage(40)
    over = today > goal
    pct = min(100, round(100 * today / goal)) if goal else 0
    return {
        "daily_goal": goal,
        "today_minutes": today,
        "weekly_by_app": weekly,
        "week_max": week_max,
        "usage_rows": usage,
        "goal_percent": pct,
        "over_goal": over,
    }


@app.route("/")
def home():
    return render_template("index.html", **_dashboard_context())


@app.route("/usage", methods=["POST"])
def add_usage():
    app_name = (request.form.get("app_name") or "").strip()
    raw_minutes = request.form.get("minutes", "").strip()
    raw_date = (request.form.get("logged_date") or "").strip()
    if raw_date:
        try:
            datetime.strptime(raw_date, "%Y-%m-%d")
        except ValueError:
            flash("Please use a valid date.", "error")
            return redirect(url_for("home"))

    if not app_name:
        flash("Please enter an app or site name.", "error")
        return redirect(url_for("home"))
    try:
        minutes = int(raw_minutes)
        if minutes < 0:
            raise ValueError
    except ValueError:
        flash("Minutes must be a non-negative whole number.", "error")
        return redirect(url_for("home"))

    try:
        db.add_usage(app_name, minutes, raw_date or None)
    except Exception:
        flash("Could not save that entry. Try again.", "error")
        return redirect(url_for("home"))

    flash("Screen time logged.", "ok")
    return redirect(url_for("home"))


@app.post("/usage/<int:entry_id>/delete")
def delete_usage(entry_id: int):
    if db.delete_usage(entry_id):
        flash("Entry removed.", "ok")
    else:
        flash("That entry was not found.", "error")
    return redirect(url_for("home"))


@app.post("/settings/goal")
def update_goal():
    raw = request.form.get("daily_goal_minutes", "").strip()
    try:
        mins = int(raw)
        if mins < 1 or mins > 24 * 60:
            raise ValueError
    except ValueError:
        flash("Daily goal must be between 1 and 1440 minutes.", "error")
        return redirect(url_for("home"))
    db.set_daily_goal_minutes(mins)
    flash("Daily screen time goal updated.", "ok")
    return redirect(url_for("home"))


@app.get("/view")
def view_legacy():
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
