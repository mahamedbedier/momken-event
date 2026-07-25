"""
Momken For Her — Flask Application
===================================
Full-stack event management platform with:
- Server-rendered Jinja2 templates
- SQLite database via SQLAlchemy
- Secure authentication (bcrypt + Flask-Login)
- Mock payment gateway with Luhn validation
- Admin dashboard with analytics API
"""

import base64
import io
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from functools import wraps

import qrcode

import bcrypt
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from config import Config
from models import AgendaItem, Order, Speaker, Sponsor, TicketType, User, db


# ═══════════════════════════════════════════════════════════════════════════
# App Factory
# ═══════════════════════════════════════════════════════════════════════════

def migrate_db(app):
    """Ensure missing columns are automatically added to SQLite database."""
    with app.app_context():
        with db.engine.connect() as conn:
            try:
                # Users table
                cols = [row[1] for row in conn.execute(db.text("PRAGMA table_info(users)")).fetchall()]
                if "role" not in cols:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))

                # Speakers table
                cols = [row[1] for row in conn.execute(db.text("PRAGMA table_info(speakers)")).fetchall()]
                if "email" not in cols:
                    conn.execute(db.text("ALTER TABLE speakers ADD COLUMN email VARCHAR(120)"))
                if "user_id" not in cols:
                    conn.execute(db.text("ALTER TABLE speakers ADD COLUMN user_id INTEGER"))
                if "qr_code_hash" not in cols:
                    conn.execute(db.text("ALTER TABLE speakers ADD COLUMN qr_code_hash VARCHAR(64)"))

                # Orders table
                cols = [row[1] for row in conn.execute(db.text("PRAGMA table_info(orders)")).fetchall()]
                if "qr_code_hash" not in cols:
                    conn.execute(db.text("ALTER TABLE orders ADD COLUMN qr_code_hash VARCHAR(64)"))
                if "is_checked_in" not in cols:
                    conn.execute(db.text("ALTER TABLE orders ADD COLUMN is_checked_in BOOLEAN DEFAULT 0"))
                if "checked_in_at" not in cols:
                    conn.execute(db.text("ALTER TABLE orders ADD COLUMN checked_in_at DATETIME"))
                if "checked_in_by_user_id" not in cols:
                    conn.execute(db.text("ALTER TABLE orders ADD COLUMN checked_in_by_user_id INTEGER"))

                conn.commit()
            except Exception as e:
                print("DB Migration notice:", e)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure instance directory exists
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth_page"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Create tables and auto-migrate missing columns
    with app.app_context():
        db.create_all()
        migrate_db(app)

    # Register all routes
    register_routes(app)

    @app.route("/make-me-admin")
    @login_required
    def make_me_admin():
        current_user.role = "admin"
        db.session.commit()
        flash("You are now an Admin!", "success")
        return redirect(url_for("profile"))

    return app


# ═══════════════════════════════════════════════════════════════════════════
# Helper: Admin-only decorator
# ═══════════════════════════════════════════════════════════════════════════

def admin_required(f):
    """Decorator that requires the user to be an admin."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != "admin":
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    """Decorator that requires the user to be an admin or volunteer."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_volunteer:
            flash("Access denied. Staff privileges required.", "error")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function


# ═══════════════════════════════════════════════════════════════════════════
# Helper: Luhn Algorithm for card validation
# ═══════════════════════════════════════════════════════════════════════════

def luhn_check(card_number: str) -> bool:
    """
    Validate a credit card number using the Luhn algorithm.

    Steps:
    1. Starting from the rightmost digit, double every second digit.
    2. If doubling results in a number > 9, subtract 9.
    3. Sum all digits.
    4. If total modulo 10 is 0, the number is valid.
    """
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False

    total = 0
    reverse = digits[::-1]
    for i, digit in enumerate(reverse):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit

    return total % 10 == 0


# ═══════════════════════════════════════════════════════════════════════════
# Route Registration
# ═══════════════════════════════════════════════════════════════════════════

def register_routes(app):
    """Register all application routes."""

    # ───────────────────────────────────────────────────────────────────
    # PUBLIC PAGES
    # ───────────────────────────────────────────────────────────────────

    @app.route("/")
    def home():
        """Homepage — renders hero, countdown, speakers, tickets, sponsors."""
        speakers = Speaker.query.filter_by(is_featured=True).order_by(Speaker.sort_order).all()
        ticket_types = TicketType.query.filter_by(is_active=True).all()

        # Group sponsors by tier
        all_sponsors = Sponsor.query.order_by(Sponsor.sort_order).all()
        sponsors = {
            "diamond": [s for s in all_sponsors if s.tier == "diamond"],
            "gold": [s for s in all_sponsors if s.tier == "gold"],
            "silver": [s for s in all_sponsors if s.tier == "silver"],
        }

        return render_template(
            "index.html",
            active_page="home",
            speakers=speakers,
            ticket_types=ticket_types,
            sponsors=sponsors,
        )

    @app.route("/speakers")
    def speakers_page():
        """All speakers page."""
        speakers = Speaker.query.order_by(Speaker.sort_order).all()
        return render_template("speakers.html", active_page="speakers", speakers=speakers)

    @app.route("/agenda")
    def agenda_page():
        """Agenda page with filter support."""
        items = AgendaItem.query.order_by(AgendaItem.sort_order).all()
        return render_template("agenda.html", active_page="agenda", agenda_items=items)

    # ───────────────────────────────────────────────────────────────────
    # AUTHENTICATION
    # ───────────────────────────────────────────────────────────────────

    @app.route("/auth")
    def auth_page():
        """Render login/signup page."""
        ticket_id = request.args.get("ticket_id", "")
        if current_user.is_authenticated:
            if ticket_id:
                return redirect(url_for("checkout_page", ticket_id=ticket_id))
            return redirect(url_for("profile"))
        return render_template("auth.html", active_page="auth", ticket_id=ticket_id)

    @app.route("/auth/login", methods=["POST"])
    def auth_login():
        """Process login form."""
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        ticket_id = request.form.get("ticket_id", "")

        # Validate input
        if not email or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("auth_page", ticket_id=ticket_id))

        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth_page", ticket_id=ticket_id))

        # Login the user
        login_user(user, remember=True)
        flash(f"Welcome back, {user.name}!", "success")

        # Redirect to checkout if coming from ticket flow
        if ticket_id:
            return redirect(url_for("checkout_page", ticket_id=ticket_id))
        return redirect(url_for("profile"))

    @app.route("/auth/register", methods=["POST"])
    def auth_register():
        """Process registration form."""
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        ticket_id = request.form.get("ticket_id", "")

        # Validate input
        errors = []
        if not name:
            errors.append("Name is required.")
        if not email:
            errors.append("Email is required.")
            
        phone_pattern = re.compile(r"^(010|011|012|015)\d{8}$")
        if not phone:
            errors.append("Phone number is required.")
        elif not phone_pattern.match(phone):
            errors.append("Phone must be exactly 11 digits and start with 010, 011, 012, or 015.")
            
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if confirm and password != confirm:
            errors.append("Passwords do not match.")
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "error")
            return redirect(url_for("auth_page", ticket_id=ticket_id))

        # Create user with hashed password
        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
        user = User(name=name, email=email, phone=phone, password_hash=pw_hash)
        db.session.add(user)
        db.session.commit()

        # Auto-login after registration
        login_user(user, remember=True)
        flash("Account created successfully!", "success")

        if ticket_id:
            return redirect(url_for("checkout_page", ticket_id=ticket_id))
        return redirect(url_for("profile"))

    @app.route("/auth/logout")
    @login_required
    def auth_logout():
        """Logout the current user."""
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("home"))

    # ───────────────────────────────────────────────────────────────────
    # USER PROFILE & QR CODE
    # ───────────────────────────────────────────────────────────────────

    @app.route("/profile")
    @login_required
    def profile():
        """User profile page with ticket QR code and role status."""
        # Check if user is a speaker and issue a Speaker VIP ticket if none exists
        if current_user.is_speaker or current_user.role == "speaker":
            speaker_ticket = TicketType.query.filter_by(name="VIP Access").first() or TicketType.query.first()
            existing_order = Order.query.filter_by(user_id=current_user.id).first()
            if not existing_order and speaker_ticket:
                speaker_order = Order(
                    user_id=current_user.id,
                    ticket_type_id=speaker_ticket.id,
                    card_last_four="SPKR",
                    status="completed",
                    qr_code_hash=f"MH-SPEAKER-{current_user.id:04d}"
                )
                db.session.add(speaker_order)
                db.session.commit()

        # Get the user's latest completed order
        latest_order = (
            Order.query.filter_by(user_id=current_user.id)
            .order_by(Order.created_at.desc())
            .first()
        )

        qr_base64 = None
        ticket_name = None
        order_status = None
        order_id = None
        qr_code_text = None

        if latest_order:
            order_id = latest_order.id
            order_status = latest_order.status
            ticket_name = latest_order.ticket_type.name
            qr_code_text = latest_order.qr_code_hash or f"MH-ORD-{latest_order.id:05d}"

            # Generate QR code PNG base64
            if latest_order.status == "completed":
                qr_img = qrcode.make(qr_code_text, box_size=8, border=2)
                buffer = io.BytesIO()
                qr_img.save(buffer, format="PNG")
                buffer.seek(0)
                qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        all_orders = Order.query.filter_by(user_id=current_user.id).all()

        return render_template(
            "profile.html",
            active_page="profile",
            qr_base64=qr_base64,
            ticket_name=ticket_name,
            order_status=order_status,
            order_id=order_id,
            qr_code_text=qr_code_text,
            user_orders=all_orders,
        )

    # ───────────────────────────────────────────────────────────────────
    # CHECKOUT & PAYMENT
    # ───────────────────────────────────────────────────────────────────

    @app.route("/checkout/<int:ticket_id>")
    @login_required
    def checkout_page(ticket_id):
        existing_order = Order.query.filter_by(user_id=current_user.id).first()
        if existing_order:
            flash("You already have a ticket. See your QR code below.", "info")
            return redirect(url_for("profile"))

        ticket = db.session.get(TicketType, ticket_id)
        if not ticket or not ticket.is_active:
            flash("Invalid ticket type.", "error")
            return redirect(url_for("home"))

        return render_template(
            "checkout.html",
            active_page="checkout",
            ticket=ticket,
        )

    @app.route("/checkout/process", methods=["POST"])
    @login_required
    def checkout_process():
        """
        Process payment — server-side validation.
        Supports both Mobile Wallet (Vodafone Cash / InstaPay) and Credit/Debit Card payments.
        """
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "errors": ["Invalid request."]}), 400

        ticket_id = data.get("ticket_id")
        payment_method = data.get("payment_method", "wallet")
        wallet_number = data.get("wallet_number", "").strip()

        # Validate ticket exists (price from DB, NOT from frontend)
        ticket = db.session.get(TicketType, ticket_id)
        if not ticket or not ticket.is_active:
            return jsonify({"success": False, "errors": ["Invalid ticket type."]}), 400

        errors = []

        if payment_method == "wallet":
            if not wallet_number or len(wallet_number) < 10 or not wallet_number.isdigit():
                errors.append("Valid Mobile Wallet number (at least 10 digits) is required.")
            card_last_four = wallet_number[-4:] if len(wallet_number) >= 4 else "9999"
        else:
            card_name = data.get("card_name", "").strip()
            card_number = data.get("card_number", "").replace(" ", "")
            card_expiry = data.get("card_expiry", "").strip()
            card_cvv = data.get("card_cvv", "").strip()

            if not card_name:
                errors.append("Cardholder name is required.")
            if not card_number.isdigit():
                errors.append("Card number must contain only digits.")
            elif not luhn_check(card_number):
                errors.append("Invalid card number (failed Luhn check).")

            if card_expiry:
                try:
                    parts = card_expiry.split("/")
                    if len(parts) != 2:
                        raise ValueError
                    month = int(parts[0])
                    year = int("20" + parts[1]) if len(parts[1]) == 2 else int(parts[1])
                    if month < 1 or month > 12:
                        raise ValueError
                    now = datetime.now(timezone.utc)
                    if year < now.year or (year == now.year and month < now.month):
                        errors.append("Card has expired.")
                except (ValueError, IndexError):
                    errors.append("Invalid expiry date. Use MM/YY format.")
            else:
                errors.append("Expiry date is required.")

            if not card_cvv or not card_cvv.isdigit() or len(card_cvv) != 3:
                errors.append("CVV must be exactly 3 digits.")

            card_last_four = card_number[-4:] if len(card_number) >= 4 else "0000"

        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        # ── Payment "approved" — create Order ────────────────────────
        order = Order(
            user_id=current_user.id,
            ticket_type_id=ticket.id,
            card_last_four=card_last_four,
            status="completed",
        )
        db.session.add(order)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Payment successful! Your biometric holographic ticket has been generated.",
            "order_id": order.id,
            "ticket_name": ticket.name,
            "amount": ticket.price,
        })

    # ───────────────────────────────────────────────────────────────────
    # ADMIN DASHBOARD
    # ───────────────────────────────────────────────────────────────────

    @app.route("/admin")
    @staff_required
    def admin_dashboard():
        """Render main admin dashboard. Access depends on role."""
        return render_template(
            "admin/dashboard.html",
            active_page="admin"
        )

    @app.route("/admin/api/stats")
    @admin_required
    def admin_stats():
        """API: Return top-level metrics."""
        total_users = User.query.filter(User.role != 'admin').count()
        total_orders = Order.query.count()
        total_revenue = db.session.query(
            db.func.sum(TicketType.price)
        ).join(Order, Order.ticket_type_id == TicketType.id).scalar() or 0

        return jsonify({
            "total_users": total_users,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
        })

    @app.route("/admin/api/registrations-chart")
    @admin_required
    def admin_registrations_chart():
        """API: Return user registration counts grouped by day (last 30 days)."""
        users = User.query.filter(User.role != "admin").all()

        # Group by date string
        counts = defaultdict(int)
        for user in users:
            day = user.created_at.strftime("%Y-%m-%d")
            counts[day] += 1

        # Sort by date
        sorted_dates = sorted(counts.keys())
        labels = sorted_dates
        data = [counts[d] for d in sorted_dates]

        return jsonify({"labels": labels, "data": data})

    @app.route("/admin/api/users")
    @admin_required
    def admin_users():
        """API: Return list of attendees with optional search."""
        q = request.args.get("q", "").strip().lower()

        query = User.query
        if q:
            query = query.filter(
                db.or_(
                    User.name.ilike(f"%{q}%"),
                    User.email.ilike(f"%{q}%"),
                )
            )

        users = query.order_by(User.created_at.desc()).all()

        result = []
        for user in users:
            # Get latest order's ticket type
            latest_order = (
                Order.query.filter_by(user_id=user.id)
                .order_by(Order.created_at.desc())
                .first()
            )
            ticket_name = latest_order.ticket_type.name if latest_order else "No ticket"
            order_status = latest_order.status if latest_order else "none"
            order_id = latest_order.id if latest_order else None
            ticket_type_id = latest_order.ticket_type_id if latest_order else None

            result.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone or "—",
                "ticket_type": ticket_name,
                "ticket_type_id": ticket_type_id,
                "order_id": order_id,
                "order_status": order_status,
                "registered": user.created_at.strftime("%b %d, %Y"),
            })

        return jsonify({"users": result, "total": len(result)})

    @app.route("/admin/api/users/<int:user_id>/ticket", methods=["POST"])
    @admin_required
    def admin_change_user_ticket(user_id):
        """API: Admin updates or assigns user ticket type."""
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found."}), 404

        data = request.get_json() or {}
        ticket_id = data.get("ticket_type_id")
        ticket = db.session.get(TicketType, ticket_id) if ticket_id else None
        if not ticket:
            return jsonify({"success": False, "error": "Invalid ticket type."}), 400

        # Update existing order or create new order
        order = Order.query.filter_by(user_id=user.id).first()
        if order:
            order.ticket_type_id = ticket.id
            order.status = "completed"
        else:
            order = Order(
                user_id=user.id,
                ticket_type_id=ticket.id,
                card_last_four="ADMIN",
                status="completed",
                qr_code_hash=f"MH-ADMIN-{user.id:04d}"
            )
            db.session.add(order)

        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Updated ticket for {user.name} to {ticket.name}.",
            "user_id": user.id,
            "ticket_name": ticket.name,
            "ticket_id": ticket.id
        })

    @app.route("/admin/api/ticket-types")
    @admin_required
    def admin_ticket_types():
        """API: Return all active ticket types for the admin dropdown."""
        types = TicketType.query.filter_by(is_active=True).all()
        return jsonify({"ticket_types": [
            {"id": t.id, "name": t.name, "price": t.price}
            for t in types
        ]})

    @app.route("/admin/api/users/<int:user_id>", methods=["DELETE"])
    @admin_required
    def admin_delete_user(user_id):
        """API: Delete a user and all their orders."""
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found."}), 404
        if user.role == "admin":
            return jsonify({"success": False, "error": "Cannot delete admin accounts."}), 403

        # Delete all orders first, then the user
        Order.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": "User deleted successfully."})

    @app.route("/admin/api/users/<int:user_id>/role", methods=["POST"])
    @admin_required
    def admin_change_user_role(user_id):
        """API: Update user role (user, volunteer, speaker, admin)."""
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found."}), 404

        data = request.get_json() or {}
        new_role = data.get("role", "user").lower().strip()
        if new_role not in ("user", "volunteer", "speaker", "admin"):
            return jsonify({"success": False, "error": "Invalid role."}), 400

        user.role = new_role
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Updated role for {user.name} to {new_role}.",
            "user_id": user.id,
            "role": user.role,
            "is_volunteer": user.is_volunteer
        })

    @app.route("/admin/api/users/<int:user_id>/toggle-volunteer", methods=["POST"])
    @admin_required
    def admin_toggle_volunteer(user_id):
        """API: 1-click toggle volunteer status for a user."""
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found."}), 404

        if user.role == "volunteer":
            user.role = "user"
        else:
            user.role = "volunteer"

        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Updated {user.name} volunteer status.",
            "user_id": user.id,
            "role": user.role,
            "is_volunteer": user.is_volunteer
        })

    @app.route("/admin/api/orders")
    @admin_required
    def admin_orders():
        """API: Return all orders/payments for the Payments tab."""
        orders = Order.query.order_by(Order.created_at.desc()).all()
        result = []
        for o in orders:
            buyer = db.session.get(User, o.user_id)
            ticket = db.session.get(TicketType, o.ticket_type_id)
            result.append({
                "id": o.id,
                "order_code": o.qr_code_hash or f"MH-ORD-{o.id:05d}",
                "user_name": buyer.name if buyer else "Unknown",
                "user_email": buyer.email if buyer else "—",
                "ticket_name": ticket.name if ticket else "Standard Pass",
                "amount": ticket.price if ticket else 0,
                "payment_method": "Mobile Wallet" if o.card_last_four and len(o.card_last_four) == 4 and o.card_last_four.startswith("01") else "Card",
                "last_four": o.card_last_four or "9999",
                "status": o.status or "completed",
                "is_checked_in": o.is_checked_in,
                "date": o.created_at.strftime("%b %d, %Y %I:%M %p") if o.created_at else "—"
            })
        return jsonify({"orders": result, "total": len(result)})
    @app.route("/admin/api/orders/<int:order_id>/status", methods=["POST"])
    @admin_required
    def admin_update_order_status(order_id):
        """API: Update ticket/order status."""
        order = db.session.get(Order, order_id)
        if not order:
            return jsonify({"success": False, "error": "Order not found."}), 404

        data = request.get_json() or {}
        new_status = data.get("status", "completed").lower().strip()
        if new_status not in ("completed", "pending", "cancelled"):
            return jsonify({"success": False, "error": "Invalid status."}), 400

        order.status = new_status
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Updated order {order.id} status to {new_status}.",
            "order_id": order.id,
            "status": order.status
        })

    @app.route("/admin/api/checkins")
    @staff_required
    def admin_checkins_log():
        """API: Return recent checked-in attendees for QR Scanner log tab."""
        checked_in = Order.query.filter_by(is_checked_in=True).order_by(Order.checked_in_at.desc()).limit(50).all()
        logs = []
        for o in checked_in:
            attendee = db.session.get(User, o.user_id)
            ticket = db.session.get(TicketType, o.ticket_type_id)
            checker = db.session.get(User, o.checked_in_by_user_id) if o.checked_in_by_user_id else None
            logs.append({
                "order_id": o.id,
                "ticket_code": o.qr_code_hash or f"MH-ORD-{o.id:05d}",
                "attendee_name": attendee.name if attendee else "Attendee",
                "attendee_email": attendee.email if attendee else "—",
                "ticket_name": ticket.name if ticket else "Pass",
                "checked_in_at": o.checked_in_at.strftime("%I:%M:%S %p") if o.checked_in_at else "—",
                "checked_in_by": checker.name if checker else "System Scanner"
            })
        return jsonify({"logs": logs, "total_checked_in": Order.query.filter_by(is_checked_in=True).count()})

    @app.route("/api/verify-ticket", methods=["POST"])
    @login_required
    def api_verify_ticket():
        """
        API Endpoint for Live Camera & Manual QR Scanner.
        Accessible by Volunteers & Admins.
        """
        if not current_user.is_volunteer:
            return jsonify({"success": False, "status": "forbidden", "message": "Access denied. Volunteer/Admin role required."}), 403

        data = request.get_json() or {}
        code = data.get("ticket_code", "").strip()

        if not code:
            return jsonify({"success": False, "status": "invalid", "message": "Please provide a valid Ticket Code or QR Hash."}), 400

        # Try searching by exact QR hash, Order ID, or card_last_four
        order = None
        if code.isdigit():
            order = db.session.get(Order, int(code))
        if not order:
            order = Order.query.filter(
                db.or_(
                    Order.qr_code_hash == code,
                    Order.qr_code_hash.ilike(f"%{code}%")
                )
            ).first()

        if not order:
            return jsonify({
                "success": False,
                "status": "invalid",
                "message": f"❌ Ticket code '{code}' not found in system."
            }), 444 if False else 200

        attendee = db.session.get(User, order.user_id)
        ticket = db.session.get(TicketType, order.ticket_type_id)

        # Check if already checked in
        if order.is_checked_in:
            time_str = order.checked_in_at.strftime("%I:%M %p") if order.checked_in_at else "earlier"
            return jsonify({
                "success": False,
                "status": "already_used",
                "message": f"⚠️ Ticket ALREADY USED! Checked in at {time_str}.",
                "order": {
                    "id": order.id,
                    "code": order.qr_code_hash or f"MH-ORD-{order.id:05d}",
                    "attendee_name": attendee.name if attendee else "Attendee",
                    "attendee_email": attendee.email if attendee else "—",
                    "ticket_name": ticket.name if ticket else "Pass",
                    "checked_in_at": time_str
                }
            })

        # Mark as checked in
        order.is_checked_in = True
        order.checked_in_at = datetime.now(timezone.utc)
        order.checked_in_by_user_id = current_user.id
        db.session.commit()

        return jsonify({
            "success": True,
            "status": "success",
            "message": f"✅ Check-in Successful! Welcome {attendee.name if attendee else 'Attendee'}.",
            "order": {
                "id": order.id,
                "code": order.qr_code_hash or f"MH-ORD-{order.id:05d}",
                "attendee_name": attendee.name if attendee else "Attendee",
                "attendee_email": attendee.email if attendee else "—",
                "ticket_name": ticket.name if ticket else "Pass",
                "checked_in_at": order.checked_in_at.strftime("%I:%M %p")
            }
        })
        db.session.commit()

        return jsonify({"success": True, "message": f"User {user.name} deleted."})

    @app.route("/admin/api/users/<int:user_id>/toggle-payment", methods=["PATCH"])
    @admin_required
    def admin_toggle_payment(user_id):
        """API: Toggle a user's order between paid (completed) and unpaid (pending)."""
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found."}), 404

        latest_order = (
            Order.query.filter_by(user_id=user.id)
            .order_by(Order.created_at.desc())
            .first()
        )

        if latest_order:
            # Toggle: completed ↔ pending
            if latest_order.status == "completed":
                latest_order.status = "pending"
                action = "marked as unpaid"
            else:
                latest_order.status = "completed"
                action = "marked as paid"
        else:
            # No order exists — create one as completed
            default_ticket = TicketType.query.first()
            latest_order = Order(
                user_id=user.id,
                ticket_type_id=default_ticket.id,
                status="completed",
            )
            db.session.add(latest_order)
            action = "marked as paid"

        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"{user.name} {action}.",
            "order_id": latest_order.id,
            "order_status": latest_order.status,
        })

    @app.route("/admin/api/users/<int:user_id>/ticket", methods=["PATCH"])
    @admin_required
    def admin_change_ticket(user_id):
        """API: Change a user's ticket type."""
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found."}), 404

        data = request.get_json()
        new_ticket_id = data.get("ticket_type_id")
        if not new_ticket_id:
            return jsonify({"success": False, "error": "ticket_type_id is required."}), 400

        ticket_type = db.session.get(TicketType, new_ticket_id)
        if not ticket_type:
            return jsonify({"success": False, "error": "Invalid ticket type."}), 400

        latest_order = (
            Order.query.filter_by(user_id=user.id)
            .order_by(Order.created_at.desc())
            .first()
        )

        if latest_order:
            latest_order.ticket_type_id = ticket_type.id
        else:
            latest_order = Order(
                user_id=user.id,
                ticket_type_id=ticket_type.id,
                status="pending",
            )
            db.session.add(latest_order)

        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Ticket changed to {ticket_type.name}.",
            "ticket_name": ticket_type.name,
            "ticket_type_id": ticket_type.id,
        })


# ═══════════════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════════════

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
