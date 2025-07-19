from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    status = db.Column(db.String(50), nullable=False, default='available')  # available, in-use, damaged, lost, maintenance
    condition = db.Column(db.String(200))
    purchase_price = db.Column(db.Float)
    current_value = db.Column(db.Float)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))