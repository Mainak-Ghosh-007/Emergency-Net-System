from flask import Flask, request, jsonify, render_template, session, redirect
from datetime import datetime
from functools import wraps
from init_db import db, User, Alert
import requests

app = Flask(__name__)
app.secret_key = "secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emergency.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"


# -------------------------
# Helpers
# -------------------------

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect("/")
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect("/")
        return func(*args, **kwargs)
    return wrapper


def haversine(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2

    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


# -------------------------
# Pages
# -------------------------

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/register_page")
def register_page():
    return render_template("register.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    return render_template("dashboard.html", user=user)


@app.route("/map")
@login_required
def map_page():
    user = User.query.get(session["user_id"])
    return render_template("map.html", user=user)


@app.route("/admin")
@admin_required
def admin():
    alerts = Alert.query.order_by(Alert.time.desc()).all()
    return render_template("admin.html", alerts=alerts)


# -------------------------
# Auth
# -------------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    user = User(
        name=data["name"],
        phone=data["phone"],
        email=data["email"],
        gender=data["gender"],
        emergency_contact=data["emergency_contact"]
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(success=True, message="Registered")


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter_by(
        phone=data["phone"]
    ).first()

    if not user:
        return jsonify(success=False, message="User not found")

    session["user_id"] = user.id

    return jsonify(
        success=True,
        message="Login successful",
        redirect="/dashboard"
    )

# ---------------------------------
# ADMIN LOGIN PAGE ROUTE
# ---------------------------------

@app.route("/admin_login_page")
def admin_login_page():
    return render_template(
        "admin_login.html"
    )


# ---------------------------------
# ADMIN LOGIN API
# ---------------------------------

@app.route(
    "/admin_login",
    methods=["POST"]
)
def admin_login():

    data = request.get_json()

    username = data.get(
        "username",
        ""
    ).strip()

    password = data.get(
        "password",
        ""
    ).strip()

    if (
        username == ADMIN_USER
        and password == ADMIN_PASS
    ):

        session.clear()

        session["is_admin"] = True

        return jsonify(
            success=True,
            message="Admin login successful",
            redirect="/admin"
        )

    return jsonify(
        success=False,
        message="Invalid username or password"
    ), 401


# ---------------------------------
# ADMIN DASHBOARD (PROTECTED)
# ---------------------------------

@app.route("/admin")
@admin_required
def admin_dashboard():

    rows = (
        db.session.query(Alert, User)
        .join(
            User,
            Alert.user_id == User.id
        )
        .order_by(
            Alert.priority.desc(),
            Alert.time.desc()
        )
        .all()
    )

    alerts = []

    for alert, user in rows:

        alerts.append(
            {
                "id": alert.id,
                "name": user.name,
                "phone": user.phone,
                "lat": alert.lat,
                "lon": alert.lon,
                "time": alert.time,
                "status": alert.status,
                "category": alert.category,
                "priority": alert.priority
            }
        )

    return render_template(
        "admin.html",
        alerts=alerts
    )


# ---------------------------------
# ADMIN LOGOUT
# ---------------------------------

@app.route("/admin_logout")
def admin_logout():

    session.clear()

    return redirect(
        "/admin_login_page"
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -------------------------
# SOS
# -------------------------

@app.route("/sos", methods=["POST"])
@login_required
def sos():
    data = request.get_json()

    alert = Alert(
        user_id=session["user_id"],
        lat=data["lat"],
        lon=data["lon"],
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        status="active"
    )

    db.session.add(alert)
    db.session.commit()

    return jsonify(success=True)


# -------------------------
# FREE LIVE MAP API
# -------------------------

@app.route("/nearby", methods=["POST"])
@login_required
def nearby():

    data = request.get_json()

    lat = float(data["lat"])
    lon = float(data["lon"])
    radius = int(data.get("radius", 10000))   # meters
    place_type = data.get("type", "hospital")

    query_map = {
        "hospital": "hospital",
        "police": "police",
        "fire_station": "fire station",
        "pharmacy": "pharmacy",
        "atm": "atm"
    }

    search_text = query_map.get(place_type, "hospital")

    # approx degree conversion
    lat_delta = radius / 111000
    lon_delta = radius / (111000 * max(0.3, abs(__import__("math").cos(__import__("math").radians(lat)))))

    left = lon - lon_delta
    right = lon + lon_delta
    top = lat + lat_delta
    bottom = lat - lat_delta

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": search_text,
        "format": "jsonv2",
        "limit": 50,
        "bounded": 1,
        "viewbox": f"{left},{top},{right},{bottom}"
    }

    headers = {
        "User-Agent": "EmergencyNet/1.0"
    }

    try:
        res = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        result = res.json()

        places = []

        for item in result:

            p_lat = float(item["lat"])
            p_lon = float(item["lon"])

            dist = haversine(lat, lon, p_lat, p_lon)

            if dist <= radius / 1000:

                places.append({
                    "name": item["display_name"].split(",")[0],
                    "lat": p_lat,
                    "lon": p_lon,
                    "distance_km": round(dist, 2)
                })

        places.sort(
            key=lambda x: x["distance_km"]
        )

        return jsonify(
            success=True,
            places=places[:20]
        )

    except Exception as e:
        return jsonify(
            success=False,
            message=str(e)
        ), 500


# -------------------------
# Run
# -------------------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)