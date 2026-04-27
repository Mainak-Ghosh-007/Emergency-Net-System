# 🚨 EmergencyNet — Emergency Response System

A full-stack emergency response web application built with Python Flask, SQLite, and Leaflet/OpenStreetMap.

## 📁 Project Structure

```
emergency_response/
├── app.py                  # Flask backend (REST API)
├── init_db.py              # Database setup + sample data
├── requirements.txt        # Python dependencies
├── emergency.db            # SQLite database (auto-created)
├── templates/
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── dashboard.html      # User dashboard
│   ├── map.html            # Live map with nearby services
│   └── admin.html          # Admin SOS alerts view
└── static/
    └── css/
        └── style.css       # Complete styling
```

## 🚀 How to Run

### Step 1 — Install Python dependencies

```bash
cd emergency_response
pip install -r requirements.txt
```

### Step 2 — Initialize the database with sample data

```bash
python init_db.py
```

This creates `emergency.db` with:
- Tables: users, alerts, places
- 40+ sample places in Kolkata (hospitals, police, metro, hotels, landmarks)
- A demo user account

### Step 3 — Run the Flask server

```bash
python app.py
```

### Step 4 — Open your browser

Go to: **http://localhost:5000**

---

## 🔑 Demo Login

| Field | Value |
|-------|-------|
| Phone | `9999999999` |

Or register a new account at http://localhost:5000/register_page

---

## 🌐 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/register` | Register a new user |
| POST | `/login` | Login by phone number |
| POST | `/sos` | Send SOS alert with GPS coordinates |
| POST | `/nearby` | Find nearest places by type |
| GET | `/alerts` | Get all SOS alerts (admin) |

### Example: POST /register
```json
{
  "name": "Ravi Kumar",
  "phone": "9876543210",
  "email": "ravi@example.com",
  "emergency_contact": "9999000000"
}
```

### Example: POST /nearby
```json
{
  "lat": 22.5726,
  "lon": 88.3639,
  "type": "hospital"
}
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    emergency_contact TEXT
);

CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    time TEXT NOT NULL
);

CREATE TABLE places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    phone TEXT
);
```

---

## ✨ Features

- **SOS Button** — One-tap emergency alert with live GPS
- **Live Map** — Leaflet + OpenStreetMap (free, no API key)
- **Nearby Search** — Haversine distance to hospitals, police, metro, hotels, landmarks
- **Emergency Calls** — Click-to-call 102, 100, 101, 1091, 108
- **Safety Mode** — Auto-send location every 30 seconds
- **Admin Panel** — View all SOS alerts at `/admin`
- **Mobile Friendly** — Responsive layout

---

## ⚠️ Notes

- Allow browser location access for GPS features
- Works on Chrome/Firefox/Edge
- No paid APIs used — fully free stack
- Sample data is for Kolkata, India — add your own city's places in `init_db.py`
