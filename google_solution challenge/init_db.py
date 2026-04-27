import os

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emergency.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# -------------------------
# Models
# -------------------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    email = db.Column(db.String(120))

    emergency_contact = db.Column(db.String(20))

    gender = db.Column(db.String(20))

    alerts = db.relationship(
        "Alert",
        backref="user",
        lazy=True
    )


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    lat = db.Column(db.Float, nullable=False)

    lon = db.Column(db.Float, nullable=False)

    time = db.Column(db.String(100))

    status = db.Column(db.String(30))

    category = db.Column(db.String(50))

    priority = db.Column(db.Integer, default=1)


class Place(db.Model):
    __tablename__ = "places"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(120),
        nullable=False
    )

    type = db.Column(
        db.String(50),
        nullable=False
    )

    lat = db.Column(db.Float, nullable=False)

    lon = db.Column(db.Float, nullable=False)

    phone = db.Column(db.String(20))


# -------------------------
# Create Database
# -------------------------

if __name__ == "__main__":

    if os.path.exists("emergency.db"):
        os.remove("emergency.db")

    with app.app_context():
        db.create_all()

    print("db ready")