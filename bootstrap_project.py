import os
from pathlib import Path

ROOT = Path(r"D:\risng water\Rising_Waters")

files = {}

# Core project files
files[ROOT / "05_Project Development Phase" / "project" / "app.py"] = '''import os
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
'''

files[ROOT / "05_Project Development Phase" / "project" / "config.py"] = '''import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.db"
MODEL_PATH = BASE_DIR / "models" / "model.pkl"
DATASET_PATH = BASE_DIR / "dataset" / "river_flood_data.csv"
MODEL_INFO_PATH = BASE_DIR / "models" / "model_info.json"
'''

files[ROOT / "05_Project Development Phase" / "project" / "requirements.txt"] = '''Flask==3.0.3\npandas==2.2.3\nnumpy==2.1.2\nscikit-learn==1.5.2\njoblib==1.4.1\nreportlab==4.0.2\nopenpyxl==3.1.2\nPillow==10.4.2\n'''

files[ROOT / "05_Project Development Phase" / "project" / "train_model.py"] = '''import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import joblib

from config import BASE_DIR, DATASET_PATH, MODEL_PATH, MODEL_INFO_PATH


def generate_dataset(path: Path, rows: int = 250) -> None:
    rng = np.random.default_rng(42)
    data = []
    for _ in range(rows):
        water_level = round(float(rng.uniform(20, 95)), 2)
        rainfall = round(float(rng.uniform(5, 80)), 2)
        temperature = round(float(rng.uniform(22, 40)), 2)
        humidity = round(float(rng.uniform(40, 95)), 2)
        river_flow = round(float(rng.uniform(20, 90)), 2)
        soil_moisture = round(float(rng.uniform(25, 85)), 2)
        water_velocity = round(float(rng.uniform(1.2, 4.8)), 2)
        previous_flood_history = int(rng.choice([0, 1, 2, 3], p=[0.7, 0.2, 0.08, 0.02]))

        if water_level > 88 or rainfall > 72 or river_flow > 85 or (water_level > 72 and previous_flood_history > 0):
            label = "Emergency"
        elif water_level > 74 or rainfall > 55 or river_flow > 70 or soil_moisture > 78:
            label = "Danger"
        elif water_level > 60 or rainfall > 35 or river_flow > 50:
            label = "Warning"
        else:
            label = "Normal"

        data.append([water_level, rainfall, temperature, humidity, river_flow, soil_moisture, water_velocity, previous_flood_history, label])

    df = pd.DataFrame(data, columns=["water_level", "rainfall", "temperature", "humidity", "river_flow", "soil_moisture", "water_velocity", "previous_flood_history", "prediction_label"])
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def train_model():
    if not DATASET_PATH.exists():
        generate_dataset(DATASET_PATH)

    df = pd.read_csv(DATASET_PATH)
    df = df.dropna()
    x = df[["water_level", "rainfall", "temperature", "humidity", "river_flow", "soil_moisture", "water_velocity", "previous_flood_history"]]
    y = df["prediction_label"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42)

    models = {
        "Random Forest": RandomForestClassifier(n_estimators=120, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, random_state=42)),
        "Support Vector Machine": make_pipeline(StandardScaler(), SVC(probability=True, random_state=42)),
    }

    results = {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        acc = accuracy_score(y_test, preds)
        results[name] = float(acc)

    best_model_name = max(results, key=results.get)
    best_model = models[best_model_name]
    best_model.fit(x, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)

    with MODEL_INFO_PATH.open("w", encoding="utf-8") as handle:
        json.dump({"best_model": best_model_name, "accuracy": results[best_model_name], "results": results}, handle, indent=2)

    print(f"Training complete. Best model: {best_model_name} with accuracy {results[best_model_name]:.2f}")


if __name__ == "__main__":
    train_model()
'''

files[ROOT / "05_Project Development Phase" / "project" / "predict.py"] = '''import json
import joblib
from pathlib import Path

from config import MODEL_PATH, MODEL_INFO_PATH


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model file is missing. Train the model first.")
    return joblib.load(MODEL_PATH)


def predict_risk(input_data):
    model = load_model()
    features = [
        input_data["water_level"],
        input_data["rainfall"],
        input_data["temperature"],
        input_data["humidity"],
        input_data["river_flow"],
        input_data["soil_moisture"],
        input_data["water_velocity"],
        input_data["previous_flood_history"],
    ]
    prediction = model.predict([features])[0]
    confidence = max(model.predict_proba([features])[0])
    risk_level = {
        "Normal": "Safe",
        "Warning": "Warning",
        "Danger": "High Risk",
        "Emergency": "Danger",
    }.get(prediction, "Safe")
    return {"prediction": prediction, "confidence": round(float(confidence), 3), "risk_level": risk_level}
'''

# Templates
files[ROOT / "05_Project Development Phase" / "project" / "templates" / "base.html"] = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rising Waters</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="sidebar">
        <div class="brand">🌊 Rising Waters</div>
        <a href="{{ url_for('dashboard') }}" class="nav-link {{ 'active' if active_page == 'dashboard' else '' }}"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
        <a href="{{ url_for('prediction') }}" class="nav-link {{ 'active' if active_page == 'prediction' else '' }}"><i class="fas fa-chart-line"></i> Prediction</a>
        <a href="{{ url_for('reports') }}" class="nav-link {{ 'active' if active_page == 'reports' else '' }}"><i class="fas fa-file-alt"></i> Reports</a>
        <a href="{{ url_for('analytics') }}" class="nav-link {{ 'active' if active_page == 'analytics' else '' }}"><i class="fas fa-chart-bar"></i> Analytics</a>
        <a href="{{ url_for('alerts') }}" class="nav-link {{ 'active' if active_page == 'alerts' else '' }}"><i class="fas fa-bell"></i> Alerts</a>
        <a href="{{ url_for('profile') }}" class="nav-link {{ 'active' if active_page == 'profile' else '' }}"><i class="fas fa-user"></i> Profile</a>
        {% if current_user and current_user['role'] == 'admin' %}
        <a href="{{ url_for('admin') }}" class="nav-link {{ 'active' if active_page == 'admin' else '' }}"><i class="fas fa-shield-alt"></i> Admin</a>
        {% endif %}
    </div>
    <div class="content">
        <nav class="topbar">
            <div class="fw-bold">AI-Based Flood Early Warning System</div>
            <div class="d-flex align-items-center gap-3">
                <button id="themeToggle" class="theme-toggle"><i class="fas fa-moon"></i></button>
                {% if current_user %}
                <span class="me-2">Welcome, {{ current_user['username'] }}</span>
                <a href="{{ url_for('logout') }}" class="btn btn-sm btn-outline-danger">Logout</a>
                {% else %}
                <a href="{{ url_for('login') }}" class="btn btn-sm btn-outline-primary">Login</a>
                {% endif %}
            </div>
        </nav>
        <main class="p-4">
            {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
            {% for category, message in messages %}
            <div class="alert alert-{{ category }} mt-2">{{ message }}</div>
            {% endfor %}
            {% endif %}
            {% endwith %}
            {% block content %}{% endblock %}
        </main>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
'''

files[ROOT / "05_Project Development Phase" / "project" / "templates" / "index.html"] = '''{% extends 'base.html' %}
{% set active_page = 'home' %}
{% block content %}
<section class="hero-card">
    <div class="row align-items-center">
        <div class="col-lg-7">
            <h1 class="display-5 fw-bold text-primary">Smart flood intelligence for safer communities</h1>
            <p class="lead">Monitor water conditions, train AI models, and receive predictive alerts before a flood becomes critical.</p>
            <div class="d-flex gap-3 mt-4">
                <a class="btn btn-primary" href="{{ url_for('register') }}">Get Started</a>
                <a class="btn btn-outline-primary" href="{{ url_for('login') }}">Sign In</a>
            </div>
        </div>
        <div class="col-lg-5">
            <img src="{{ url_for('static', filename='images/hero.png') }}" class="img-fluid rounded shadow" alt="Flood monitoring dashboard">
        </div>
    </div>
</section>
<section class="row g-4 mt-3">
    <div class="col-md-6 col-xl-3">
        <div class="card stat-card shadow-sm">
            <div class="card-body">
                <h5><i class="fas fa-user-shield"></i> Users</h5>
                <h2>{{ total_users }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-6 col-xl-3">
        <div class="card stat-card shadow-sm">
            <div class="card-body">
                <h5><i class="fas fa-chart-line"></i> Predictions</h5>
                <h2>{{ total_predictions }}</h2>
            </div>
        </div>
    </div>
</section>
{% endblock %}
'''

files[ROOT / "05_Project Development Phase" / "project" / "templates" / "login.html"] = '''{% extends 'base.html' %}
{% set active_page = 'login' %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow-sm p-4">
            <h3 class="mb-4">Login</h3>
            <form method="post">
                <div class="mb-3">
                    <label class="form-label">Username</label>
                    <input name="username" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Password</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <button class="btn btn-primary w-100">Sign In</button>
            </form>
            <div class="mt-3 d-flex justify-content-between">
                <a href="{{ url_for('register') }}">Create account</a>
                <a href="{{ url_for('forgot_password') }}">Forgot password</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

files[ROOT / "05_Project Development Phase" / "project" / "templates" / "register.html"] = '''{% extends 'base.html' %}
{% set active_page = 'register' %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-7">
        <div class="card shadow-sm p-4">
            <h3 class="mb-4">Register</h3>
            <form method="post">
                <div class="row g-3">
                    <div class="col-md-6">
                        <label class="form-label">Username</label>
                        <input name="username" class="form-control" required>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Email</label>
                        <input type="email" name="email" class="form-control" required>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Password</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Phone</label>
                        <input name="phone" class="form-control">
                    </div>
                    <div class="col-12">
                        <label class="form-label">Location</label>
                        <input name="location" class="form-control">
                    </div>
                </div>
                <button class="btn btn-primary mt-3 w-100">Create Account</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
'''

files[ROOT / "05_Project Development Phase" / "project" / "templates" / "forgot_password.html"] = '''{% extends 'base.html' %}
{% set active_page = 'forgot' %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow-sm p-4">
            <h3 class="mb-3">Forgot Password</h3>
            <form method="post">
                <div class="mb-3">
                    <label class="form-label">Email Address</label>
                    <input type="email" name="email" class="form-control" required>
                </div>
                <button class="btn btn-primary w-100">Reset Password</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
'''

files[ROOT / "05_Project Development Phase" / "project" / "templates" / "dashboard.html"] = '''{% extends 'base.html' %}
{% set active_page = 'dashboard' %}
{% block content %}
<div class="row g-4">
    <div class="col-xl-3 col-md-6">
        <div class="card stat-card shadow-sm">
            <div class="card-body">
                <h6 class="text-muted">Current Water Level</h6>
                <h2>{{ latest.water_level }} m</h2>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6">
        <div class="card stat-card shadow-sm">
            <div class="card-body">
                <h6 class="text-muted">Water Level Percentage</h6>
                <h2>{{ level_percentage }}%</h2>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6">
        <div class="card stat-card shadow-sm">
            <div class="card-body">
                <h6 class="text-muted">Rainfall</h6>
                <h2>{{ latest.rainfall }} mm</h2>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6">
        <div class="card stat-card shadow-sm">
            <div class="card-body">
                <h6 class="text-muted">Prediction</h6>
                <h2>{{ latest.prediction_label }}</h2>
            </div>
        </div>
    </div>
</div>
<div class="row g-4 mt-2">
    <div class="col-lg-8">
        <div class="card shadow-sm p-3">
            <h5>Live Water Trend</h5>
            <canvas id="trendChart" height="200"></canvas>
        </div>
    </div>
    <div class="col-lg-4">
        <div class="card shadow-sm p-3">
            <h5>Recent Alerts</h5>
            <ul class="list-group list-group-flush">
                {% for alert in recent_alerts %}
                <li class="list-group-item"><strong>{{ alert.severity }}</strong> - {{ alert.message }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
</div>
<div class="row g-4 mt-2">
    <div class="col-lg-8">
        <div class="card shadow-sm p-3">
            <h5>Prediction History</h5>
            <table class="table table-sm">
                <thead><tr><th>Time</th><th>Risk</th><th>Confidence</th></tr></thead>
                <tbody>
                    {% for row in history %}
                    <tr><td>{{ row.created_at }}</td><td>{{ row.prediction_label }}</td><td>{{ row.confidence }}</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    <div class="col-lg-4">
        <div class="card shadow-sm p-3">
            <h5>Current Status</h5>
            <p><strong>Risk Level:</strong> {{ latest.risk_level }}</p>
            <p><strong>Temperature:</strong> {{ latest.temperature }}°C</p>
            <p><strong>Humidity:</strong> {{ latest.humidity }}%</p>
            <p><strong>River Flow:</strong> {{ latest.river_flow }} m³/s</p>
            <p><strong>Last Updated:</strong> {{ latest.created_at }}</p>
        </div>
    </div>
</div>
<script>
const trendCtx = document.getElementById('trendChart');
new Chart(trendCtx, {
  type: 'line',
  data: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'Water Level',
      data: [54, 58, 62, 70, 74, 79, 82],
      borderColor: '#0d6efd',
      tension: 0.3,
      fill: true,
      backgroundColor: 'rgba(13,110,253,0.15)'
    }]
  },
  options: { responsive: true }
});
</script>
{% endblock %}
'''

files[ROOT / "05_Project Development Phase" / "project" / "templates" / "prediction.html"] = '''{% extends 'base.html' %}
{% set active_page = 'prediction' %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="card shadow-sm p-4">
            <h3 class="mb-4">Flood Prediction Form</h3>
            <form method="post">
                <div class="row g-3">
                    <div class="col-md-6"><label class="form-label">Water Level</label><input type="number" step="0.1" name="water_level" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">Rainfall</label><input type="number" step="0.1" name="rainfall" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">Temperature</label><input type="number" step="0.1" name="temperature" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">Humidity</label><input type="number" step="0.1" name="humidity" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">River Flow</label><input type="number" step="0.1" name="river_flow" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">Soil Moisture</label><input type="number" step="0.1" name="soil_moisture" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">Water Velocity</label><input type="number" step="0.1" name="water_velocity" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">Previous Flood History</label><input type="number" step="1" name="previous_flood_history" class="form-control" required></div>
                </div>
                <button class="btn btn-primary mt-4">Run Prediction</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
'''

files[ROOT / "05_Project Development Phase" / "project" / "templates" / "reports.html"] = '''{% extends 'base.html' %}
{% set active_page = 'reports' %}
{% block content %}
<div class="card shadow-sm p-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h3>Prediction Reports</h3>
        <div>
            <a class="btn btn-outline-primary" href="{{ url_for('export_data', kind='csv') }}">Export CSV</a>
            <a class="btn btn-outline-success" href="{{ url_for('export_data', kind='json') }}">Export JSON</a>
        </div>
    </div>
    <table class="table table-hover">
        <thead><tr><th>ID</th><th>Water Level</th><th>Prediction</th><th>Risk</th><th>Date</th></tr></thead>
        <tbody>
            {% for row in rows %}
            <tr><td>{{ row.id }}</td><td>{{ row.water_level }}</td><td>{{ row.prediction_label }}</td><td>{{ row.risk_level }}</td><td>{{ row.created_at }}</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
'''

files[ROOT / "05_Project Development Phase" / "project" / "templates" / "analytics.html"] = '''{% extends 'base.html' %}
{% set active_page = 'analytics' %}
{% block content %}
<div class="row g-4">
    <div class="col-lg-7">
        <div class="card shadow-sm p-3">
            <h5>Risk Distribution</h5>
            <canvas id="pieChart" height="220"></canvas>
        </div>
    </div>
    <div class="col-lg-5">
        <div class="card shadow-sm p-3">
            <h5>Monthly Report</h5>
            <ul class="list-group list-group-flush">
                {% for key, value in counts.items() %}
                <li class="list-group-item d-flex justify-content-between"><span>{{ key }}</span><strong>{{ value }}</strong></li>
                {% endfor %}
            </ul>
        </div>
    </div>
</div>
<script>
const pieCtx = document.getElementById('pieChart');
new Chart(pieCtx, {
  type: 'pie',
  data: {
    labels: {{ counts.keys() | list | tojson }},
    datasets: [{ data: {{ counts.values() | list | tojson }}, backgroundColor: ['#0d6efd', '#ffc107', '#fd7e14', '#dc3545'] }]
  }
});
</script>
{% endblock %}
'''

files[ROOT / "05_Project Development Phase" / "project" / "templates" / "alerts.html"] = '''{% extends 'base.html' %}
{% set active_page = 'alerts' %}
{% block content %}
<div class="card shadow-sm p-4">
    <h3>Alert Center</h3>
    <div class="list-group mt-3">
        {% for row in rows %}
        <div class="list-group-item">
            <div class="d-flex justify-content-between">
                <strong>{{ row.severity }}</strong>
                <small>{{ row.created_at }}</small>
            </div>
            <p class="mb-0">{{ row.message }}</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
'''

files[ROOT / "05_Project Development Phase" / "project" / "templates" / "profile.html"] = '''{% extends 'base.html' %}
{% set active_page = 'profile' %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-7">
        <div class="card shadow-sm p-4">
            <h3>Profile</h3>
            <form method="post">
                <div class="mb-3"><label class="form-label">Username</label><input class="form-control" value="{{ user.username }}" disabled></div>
                <div class="mb-3"><label class="form-label">Email</label><input class="form-control" value="{{ user.email }}" disabled></div>
                <div class="mb-3"><label class="form-label">Phone</label><input name="phone" class="form-control" value="{{ user.phone or '' }}"></div>
                <div class="mb-3"><label class="form-label">Location</label><input name="location" class="form-control" value="{{ user.location or '' }}"></div>
                <button class="btn btn-primary">Save Changes</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
'''

files[ROOT / "05_Project Development Phase" / "project" / "templates" / "admin.html"] = '''{% extends 'base.html' %}
{% set active_page = 'admin' %}
{% block content %}
<div class="row g-4">
    <div class="col-lg-6">
        <div class="card shadow-sm p-4">
            <h4>User Management</h4>
            <ul class="list-group mt-3">
                {% for user in users %}
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <span>{{ user.username }} ({{ user.role }})</span>
                    <form method="post" action="{{ url_for('delete_user', user_id=user.id) }}">
                        <button class="btn btn-sm btn-danger">Delete</button>
                    </form>
                </li>
                {% endfor %}
            </ul>
        </div>
    </div>
    <div class="col-lg-6">
        <div class="card shadow-sm p-4">
            <h4>Prediction Logs</h4>
            <ul class="list-group mt-3">
                {% for item in predictions %}
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <span>{{ item.prediction_label }} - {{ item.risk_level }}</span>
                    <form method="post" action="{{ url_for('delete_prediction', prediction_id=item.id) }}">
                        <button class="btn btn-sm btn-danger">Delete</button>
                    </form>
                </li>
                {% endfor %}
            </ul>
        </div>
    </div>
</div>
{% endblock %}
'''

# Static files
files[ROOT / "05_Project Development Phase" / "project" / "static" / "css" / "style.css"] = '''body { background: #f4f8ff; color: #10304d; font-family: "Segoe UI", sans-serif; }
.sidebar { width: 250px; background: linear-gradient(135deg, #063970, #0d6efd); color: white; min-height: 100vh; position: fixed; padding: 20px 15px; }
.content { margin-left: 250px; min-height: 100vh; }
.topbar { background: white; padding: 15px 25px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.brand { font-size: 1.3rem; font-weight: bold; margin-bottom: 25px; }
.nav-link { color: white; text-decoration: none; display: block; padding: 10px 12px; border-radius: 8px; margin-bottom: 6px; }
.nav-link:hover, .nav-link.active { background: rgba(255,255,255,0.18); }
.hero-card { background: linear-gradient(135deg, #eaf4ff, #fff); border-radius: 20px; padding: 25px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.stat-card { border: none; border-radius: 16px; background: linear-gradient(145deg, #ffffff, #eef5ff); }
.theme-toggle { border: none; background: #f3f7ff; border-radius: 50%; width: 40px; height: 40px; }
body.dark { background: #0f172a; color: #e2e8f0; }
body.dark .topbar, body.dark .card, body.dark .hero-card { background: #111827; color: #e2e8f0; }
body.dark .sidebar { background: linear-gradient(135deg, #020617, #1d4ed8); }
'''

files[ROOT / "05_Project Development Phase" / "project" / "static" / "js" / "app.js"] = '''document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      document.body.classList.toggle("dark");
      const icon = toggle.querySelector("i");
      icon.className = document.body.classList.contains("dark") ? "fas fa-sun" : "fas fa-moon";
    });
  }
});
'''

# README and documentation
files[ROOT / "05_Project Development Phase" / "project" / "README.md"] = '''# AI-Based Rising Water Detection and Flood Early Warning System

## Project Overview
This project provides an AI-powered flood early warning system that monitors water and weather indicators, predicts flood severity using machine learning, and displays a modern dashboard for analysis and alerts.

## Objectives
- Detect rising water risks using machine learning.
- Provide a responsive dashboard for monitoring and alerts.
- Support user authentication and admin operations.
- Store and analyze historical prediction data.

## Features
- Authentication and session management
- Dashboard with real-time metrics
- Prediction engine with trained ML model
- Analytics and reporting
- Admin panel for managing users and logs

## Technologies Used
- Frontend: HTML, CSS, Bootstrap, JavaScript, Chart.js
- Backend: Flask, Python
- ML: Pandas, NumPy, Scikit-learn, Joblib
- Database: SQLite

## Installation
1. `cd 05_Project Development Phase/project`
2. `pip install -r requirements.txt`
3. `python train_model.py`
4. `python app.py`

## Folder Structure
- `dataset/` contains synthetic flood data.
- `models/` stores the trained model.
- `templates/` contains the UI pages.
- `static/` contains styles and scripts.

## Dataset Description
The dataset contains water level, rainfall, temperature, humidity, river flow, soil moisture, water velocity, flood history, and prediction labels.

## Machine Learning Workflow
1. Generate dataset
2. Clean and preprocess data
3. Train multiple classifiers
4. Compare accuracy
5. Save the best model as `models/model.pkl`

## Screenshots
The demonstration folder contains sample dashboard and prediction screenshots.

## Future Scope
- Real sensor integration
- SMS and email alerts
- GIS mapping and geospatial analysis

## Team Members
- Team Lead: SmartBridge Project Team
- Developer: Full Stack + AI/ML Engineer

## License
This project is developed for educational and demonstration purposes.
'''

# Root documentation folders and placeholder files
files[ROOT / "01_Brainstorming & Ideation" / "Problem Statement.pdf"] = ""
files[ROOT / "01_Brainstorming & Ideation" / "Brainstorming.pdf"] = ""
files[ROOT / "01_Brainstorming & Ideation" / "Literature Survey.pdf"] = ""
files[ROOT / "01_Brainstorming & Ideation" / "Existing System.pdf"] = ""
files[ROOT / "01_Brainstorming & Ideation" / "Proposed System.pdf"] = ""
files[ROOT / "01_Brainstorming & Ideation" / "Mind Map.pdf"] = ""
files[ROOT / "02_Requirement Analysis" / "Requirement Analysis.pdf"] = ""
files[ROOT / "02_Requirement Analysis" / "Functional Requirements.pdf"] = ""
files[ROOT / "02_Requirement Analysis" / "Non Functional Requirements.pdf"] = ""
files[ROOT / "02_Requirement Analysis" / "Software Requirements.pdf"] = ""
files[ROOT / "02_Requirement Analysis" / "Hardware Requirements.pdf"] = ""
files[ROOT / "02_Requirement Analysis" / "Use Case Diagram.png"] = ""
files[ROOT / "02_Requirement Analysis" / "Use Case Description.pdf"] = ""
files[ROOT / "03_Project Design Phase" / "System Architecture.png"] = ""
files[ROOT / "03_Project Design Phase" / "Flowchart.png"] = ""
files[ROOT / "03_Project Design Phase" / "Data Flow Diagram.png"] = ""
files[ROOT / "03_Project Design Phase" / "ER Diagram.png"] = ""
files[ROOT / "03_Project Design Phase" / "Sequence Diagram.png"] = ""
files[ROOT / "03_Project Design Phase" / "Activity Diagram.png"] = ""
files[ROOT / "03_Project Design Phase" / "Class Diagram.png"] = ""
files[ROOT / "03_Project Design Phase" / "Database Design.pdf"] = ""
files[ROOT / "03_Project Design Phase" / "UI Design.pdf"] = ""
files[ROOT / "04_Project Planning Phase" / "Project Plan.pdf"] = ""
files[ROOT / "04_Project Planning Phase" / "Sprint Planning.pdf"] = ""
files[ROOT / "04_Project Planning Phase" / "Timeline.pdf"] = ""
files[ROOT / "04_Project Planning Phase" / "Gantt Chart.png"] = ""
files[ROOT / "04_Project Planning Phase" / "Work Breakdown Structure.pdf"] = ""
files[ROOT / "04_Project Planning Phase" / "Risk Analysis.pdf"] = ""
files[ROOT / "06_Project Testing" / "Test Plan.pdf"] = ""
files[ROOT / "06_Project Testing" / "Unit Testing.pdf"] = ""
files[ROOT / "06_Project Testing" / "Integration Testing.pdf"] = ""
files[ROOT / "06_Project Testing" / "System Testing.pdf"] = ""
files[ROOT / "06_Project Testing" / "Test Cases.xlsx"] = ""
files[ROOT / "06_Project Testing" / "Bug Report.pdf"] = ""
files[ROOT / "06_Project Testing" / "Screenshots"] = ""
files[ROOT / "07_Project Documentation" / "Final Project Report.pdf"] = ""
files[ROOT / "07_Project Documentation" / "IEEE Research Paper.pdf"] = ""
files[ROOT / "07_Project Documentation" / "User Manual.pdf"] = ""
files[ROOT / "07_Project Documentation" / "Installation Guide.pdf"] = ""
files[ROOT / "07_Project Documentation" / "Deployment Guide.pdf"] = ""
files[ROOT / "07_Project Documentation" / "API Documentation.pdf"] = ""
files[ROOT / "08_Project Demonstration" / "Dashboard Screenshots"] = ""
files[ROOT / "08_Project Demonstration" / "Prediction Screenshots"] = ""
files[ROOT / "08_Project Demonstration" / "Testing Screenshots"] = ""
files[ROOT / "08_Project Demonstration" / "Output Screenshots"] = ""
files[ROOT / "08_Project Demonstration" / "Project Images"] = ""

# Create directories and files
for path, content in files.items():
    if path.suffix == "":
        path.mkdir(parents=True, exist_ok=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        if content:
            path.write_text(content, encoding="utf-8")
        else:
            path.write_bytes(b"")

print("Project bootstrap complete")
