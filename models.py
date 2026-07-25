"""
SQLAlchemy database models for the Momken For Her platform.

Tables: User, TicketType, Order, Speaker, Sponsor, AgendaItem
"""

from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Registered attendee, volunteer, speaker, or admin user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")  # "user", "volunteer", "speaker", "admin"
    
    # Demographics & Registration Data
    city = db.Column(db.String(100), nullable=True)
    university = db.Column(db.String(150), nullable=True)
    faculty = db.Column(db.String(150), nullable=True)
    academic_status = db.Column(db.String(50), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    source = db.Column(db.String(100), nullable=True)
    why_attending = db.Column(db.String(300), nullable=True)
    hopes_gained = db.Column(db.String(300), nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    orders = db.relationship("Order", foreign_keys="Order.user_id", backref="user", lazy=True)

    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == "admin"

    @property
    def is_volunteer(self):
        """Check if user has volunteer permissions."""
        return self.role in ("volunteer", "admin")

    @property
    def is_speaker(self):
        """Check if user is a speaker."""
        return self.role == "speaker"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class TicketType(db.Model):
    """Available ticket tiers (Standard, VIP, Coaching)."""

    __tablename__ = "ticket_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # Price in EGP
    description = db.Column(db.Text, nullable=True)
    badge = db.Column(db.String(20), nullable=True)  # "VIP", "Limited Spots", etc.
    is_active = db.Column(db.Boolean, default=True)

    orders = db.relationship("Order", backref="ticket_type", lazy=True)

    def __repr__(self):
        return f"<TicketType {self.name} - {self.price} EGP>"


class Order(db.Model):
    """A completed ticket purchase or speaker pass."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ticket_type_id = db.Column(db.Integer, db.ForeignKey("ticket_types.id"), nullable=False)
    card_last_four = db.Column(db.String(4), nullable=True)
    status = db.Column(db.String(20), default="completed")
    qr_code_hash = db.Column(db.String(64), unique=True, nullable=True)
    is_checked_in = db.Column(db.Boolean, default=False)
    checked_in_at = db.Column(db.DateTime, nullable=True)
    checked_in_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    checked_in_by = db.relationship("User", foreign_keys=[checked_in_by_user_id])

    def __repr__(self):
        return f"<Order #{self.id} - User {self.user_id}>"


class Speaker(db.Model):
    """Event speaker profile."""

    __tablename__ = "speakers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    qr_code_hash = db.Column(db.String(64), unique=True, nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Speaker {self.name}>"

    @property
    def initials(self):
        """Generate initials from name for avatar placeholder."""
        parts = self.name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.name[0].upper()


class Sponsor(db.Model):
    """Event sponsor / partner."""

    __tablename__ = "sponsors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tier = db.Column(db.String(20), nullable=False)  # "diamond", "gold", "silver"
    logo_filename = db.Column(db.String(200), nullable=True)
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Sponsor {self.name} ({self.tier})>"


class AgendaItem(db.Model):
    """A single session or event in the agenda."""

    __tablename__ = "agenda_items"

    id = db.Column(db.Integer, primary_key=True)
    time_start = db.Column(db.String(20), nullable=False)
    time_end = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    speakers_text = db.Column(db.String(500), nullable=True)
    stage = db.Column(db.String(20), nullable=False)  # "main", "secondary", "workshop"
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<AgendaItem {self.title[:40]}>"
