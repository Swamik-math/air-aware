from datetime import datetime

from app.extensions import db


class RouteHistory(db.Model):
    __tablename__ = "route_history"

    id = db.Column(db.Integer, primary_key=True)
    source_lat = db.Column(db.Float, nullable=False)
    source_lon = db.Column(db.Float, nullable=False)
    destination_lat = db.Column(db.Float, nullable=False)
    destination_lon = db.Column(db.Float, nullable=False)
    preference = db.Column(db.String(20), nullable=False)
    shortest_summary = db.Column(db.JSON, nullable=True)
    fastest_summary = db.Column(db.JSON, nullable=True)
    healthiest_summary = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
