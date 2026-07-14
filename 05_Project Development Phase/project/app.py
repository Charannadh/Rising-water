import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for

from config import BASE_DIR, DATABASE_PATH, MODEL_PATH, DATASET_PATH
from predict import predict_risk

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "smartbridge-flood-warning-system"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            phone TEXT,
            location TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            water_level REAL,
            rainfall REAL,
            temperature REAL,
            humidity REAL,
            river_flow REAL,
            soil_moisture REAL,
            water_velocity REAL,
            previous_flood_history REAL,
            prediction_label TEXT,
            confidence REAL,
            risk_level TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            severity TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def seed_demo_data():
    conn = get_db_connection()
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        conn.execute(
            "INSERT INTO users (username, email, password, role, phone, location, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("admin", "admin@smartbridge.com", "Admin@123", "admin", "+91-9000000000", "Hyderabad", datetime.now().isoformat()),
        )
        conn.execute(
            "INSERT INTO users (username, email, password, role, phone, location, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("demo", "demo@smartbridge.com", "Demo@123", "user", "+91-9111111111", "Chennai", datetime.now().isoformat()),
        )
    prediction_count = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    if prediction_count == 0:
        sample_rows = [
            (68.5, 22.0, 32.0, 54.0, 44.5, 61.0, 2.8, 0.0, "Warning", 0.78, "Warning", datetime.now().isoformat()),
            (82.4, 48.0, 35.0, 61.0, 58.7, 69.0, 3.6, 1.0, "Danger", 0.84, "High Risk", datetime.now().isoformat()),
            (74.2, 33.0, 30.0, 57.0, 49.0, 64.0, 3.1, 0.0, "Warning", 0.81, "Warning", datetime.now().isoformat()),
        ]
        conn.executemany(
            "INSERT INTO predictions (water_level, rainfall, temperature, humidity, river_flow, soil_moisture, water_velocity, previous_flood_history, prediction_label, confidence, risk_level, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            sample_rows,
        )
    alert_count = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    if alert_count == 0:
        conn.execute(
            "INSERT INTO alerts (user_id, message, severity, created_at) VALUES (?, ?, ?, ?)",
            (1, "Water level rising near the monitoring station.", "High", datetime.now().isoformat()),
        )
        conn.execute(
            "INSERT INTO alerts (user_id, message, severity, created_at) VALUES (?, ?, ?, ?)",
            (2, "Heavy rainfall detected; warning threshold reached.", "Warning", datetime.now().isoformat()),
        )
    conn.commit()
    conn.close()


init_db()
seed_demo_data()


def require_login():
    if "user_id" not in session:
        flash("Please login to continue.", "warning")
        return False
    return True


@app.context_processor
def inject_user():
    user = None
    if "user_id" in session:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        conn.close()
    return {"current_user": user}


@app.route("/")
def index():
    conn = get_db_connection()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_predictions = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    conn.close()
    return render_template("index.html", total_users=total_users, total_predictions=total_predictions)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        phone = request.form.get("phone", "").strip()
        location = request.form.get("location", "").strip()
        if not username or not email or not password:
            flash("Please fill all required fields.", "warning")
            return redirect(url_for("register"))
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, email, password, phone, location, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (username, email, password, phone, location, datetime.now().isoformat()),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("Username or email already exists.", "danger")
            return redirect(url_for("register"))
        conn.close()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user:
            flash("Password reset is not enabled in demo mode. Use password: Demo@123", "info")
        else:
            flash("No account found with that email.", "danger")
        return redirect(url_for("forgot_password"))
    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You logged out successfully.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("login"))
    conn = get_db_connection()
    latest = conn.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 1").fetchone()
    recent_alerts = conn.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 5").fetchall()
    history = conn.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 8").fetchall()
    conn.close()
    if latest is None:
        latest = {
            "water_level": 0,
            "rainfall": 0,
            "temperature": 0,
            "humidity": 0,
            "river_flow": 0,
            "prediction_label": "Safe",
            "risk_level": "Safe",
            "created_at": datetime.now().isoformat(),
        }
    level_percentage = min(100, round((latest["water_level"] / 100) * 100, 1))
    return render_template(
        "dashboard.html",
        latest=latest,
        level_percentage=level_percentage,
        recent_alerts=recent_alerts,
        history=history,
    )


@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    if not require_login():
        return redirect(url_for("login"))
    if request.method == "POST":
        data = {
            "water_level": float(request.form.get("water_level", 0)),
            "rainfall": float(request.form.get("rainfall", 0)),
            "temperature": float(request.form.get("temperature", 0)),
            "humidity": float(request.form.get("humidity", 0)),
            "river_flow": float(request.form.get("river_flow", 0)),
            "soil_moisture": float(request.form.get("soil_moisture", 0)),
            "water_velocity": float(request.form.get("water_velocity", 0)),
            "previous_flood_history": float(request.form.get("previous_flood_history", 0)),
        }
        result = predict_risk(data)
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO predictions (user_id, water_level, rainfall, temperature, humidity, river_flow, soil_moisture, water_velocity, previous_flood_history, prediction_label, confidence, risk_level, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                session["user_id"],
                data["water_level"],
                data["rainfall"],
                data["temperature"],
                data["humidity"],
                data["river_flow"],
                data["soil_moisture"],
                data["water_velocity"],
                data["previous_flood_history"],
                result["prediction"],
                result["confidence"],
                result["risk_level"],
                datetime.now().isoformat(),
            ),
        )
        conn.execute(
            "INSERT INTO alerts (user_id, message, severity, created_at) VALUES (?, ?, ?, ?)",
            (session["user_id"], f"{result['prediction']} risk detected with confidence {result['confidence']:.2f}.", result["risk_level"], datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
        flash(f"Prediction completed: {result['prediction']} ({result['risk_level']})", "success")
        return redirect(url_for("prediction"))
    return render_template("prediction.html")


@app.route("/reports")
def reports():
    if not require_login():
        return redirect(url_for("login"))
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 10").fetchall()
    conn.close()
    return render_template("reports.html", rows=rows)


@app.route("/analytics")
def analytics():
    if not require_login():
        return redirect(url_for("login"))
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 20").fetchall()
    conn.close()
    labels = [row["prediction_label"] for row in rows]
    counts = {label: labels.count(label) for label in set(labels)}
    return render_template("analytics.html", rows=rows, counts=counts)


@app.route("/alerts")
def alerts():
    if not require_login():
        return redirect(url_for("login"))
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM alerts ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("alerts.html", rows=rows)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not require_login():
        return redirect(url_for("login"))
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    if request.method == "POST":
        phone = request.form.get("phone", "")
        location = request.form.get("location", "")
        conn.execute("UPDATE users SET phone = ?, location = ? WHERE id = ?", (phone, location, session["user_id"]))
        conn.commit()
        flash("Profile updated.", "success")
        conn.close()
        return redirect(url_for("profile"))
    conn.close()
    return render_template("profile.html", user=user)


@app.route("/admin")
def admin():
    if not require_login() or session.get("role") != "admin":
        flash("Only administrators can access this page.", "danger")
        return redirect(url_for("dashboard"))
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    predictions = conn.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 20").fetchall()
    conn.close()
    return render_template("admin.html", users=users, predictions=predictions)


@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash("User deleted.", "success")
    return redirect(url_for("admin"))


@app.route("/admin/delete_prediction/<int:prediction_id>", methods=["POST"])
def delete_prediction(prediction_id):
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))
    conn = get_db_connection()
    conn.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
    conn.commit()
    conn.close()
    flash("Prediction deleted.", "success")
    return redirect(url_for("admin"))


@app.route("/export/<kind>")
def export_data(kind):
    if not require_login():
        return redirect(url_for("login"))
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM predictions ORDER BY created_at DESC").fetchall()
    conn.close()
    if kind == "csv":
        output = "id,water_level,rainfall,temperature,humidity,river_flow,prediction_label,confidence,risk_level,created_at\n"
        for row in rows:
            output += f"{row['id']},{row['water_level']},{row['rainfall']},{row['temperature']},{row['humidity']},{row['river_flow']},{row['prediction_label']},{row['confidence']},{row['risk_level']},{row['created_at']}\n"
        path = Path(BASE_DIR) / "exports" / "predictions.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")
        return send_file(path, as_attachment=True, download_name="predictions.csv")
    if kind == "json":
        path = Path(BASE_DIR) / "exports" / "predictions.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([dict(row) for row in rows], indent=2), encoding="utf-8")
        return send_file(path, as_attachment=True, download_name="predictions.json")
    return redirect(url_for("reports"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
