from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    trips = db.relationship('Trip', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    cover_photo = db.Column(db.String(255))
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    stops = db.relationship('Stop', backref='trip', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='trip', lazy=True, cascade='all, delete-orphan')
    checklist_items = db.relationship('ChecklistItem', backref='trip', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='trip', lazy=True, cascade='all, delete-orphan')

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    cost_index = db.Column(db.String(20)) # e.g., '$', '$$', '$$$'
    popularity = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)

    stops = db.relationship('Stop', backref='city', lazy=True)
    activities = db.relationship('Activity', backref='city', lazy=True)

class Stop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    order_index = db.Column(db.Integer, nullable=False)

    stop_activities = db.relationship('StopActivity', backref='stop', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='stop', lazy=True, cascade='all, delete-orphan')

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50)) # e.g., 'Food', 'Sightseeing'
    cost = db.Column(db.Float)
    duration = db.Column(db.Integer) # in minutes
    description = db.Column(db.Text)

    stop_activities = db.relationship('StopActivity', backref='activity', lazy=True)

class StopActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey('stop.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    scheduled_date = db.Column(db.Date)
    scheduled_time = db.Column(db.Time)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False) # e.g., 'Transport', 'Accommodation'
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    description = db.Column(db.String(255))

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    is_packed = db.Column(db.Boolean, default=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    stop_id = db.Column(db.Integer, db.ForeignKey('stop.id'), nullable=True) # Optional link to specific stop
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
