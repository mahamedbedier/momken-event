"""
Database seeder — populates all tables with data from the original prototype.

Usage:
    python seed.py
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import bcrypt

# ── Bootstrap Flask app for DB access ──────────────────────────────────────
# Add project root to path so imports work when running as script
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app  # noqa: E402
from models import (  # noqa: E402
    AgendaItem,
    Order,
    Speaker,
    Sponsor,
    TicketType,
    User,
    db,
)

app = create_app()


def hash_password(plain: str) -> str:
    """Hash a password with bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def seed():
    """Drop and recreate all tables, then seed with sample data."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("[*] Tables created.")

        # ── 1. Ticket Types ──────────────────────────────────────────────
        tickets = [
            TicketType(
                name="Standard Ticket",
                price=200,
                description="Access to general sessions and training workshops.",
                badge=None,
            ),
            TicketType(
                name="VIP Ticket",
                price=300,
                description="Access to exclusive VIP sessions, advanced VIP workshops, and networking zones.",
                badge="VIP",
            ),
            TicketType(
                name="Coaching & Mentoring",
                price=600,
                description="Exclusive access to intensive Coaching Circles. (1:1 Mentoring available for 250 EGP).",
                badge="Limited Spots",
            ),
        ]
        db.session.add_all(tickets)
        print("[+] 3 ticket types seeded.")

        # ── 2. Admin User ────────────────────────────────────────────────
        admin = User(
            name="Admin",
            email="admin@momken.com",
            phone="01000000000",
            password_hash=hash_password("admin123"),
            is_admin=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        )
        db.session.add(admin)

        # ── 3. Sample Attendees (for chart demo) ─────────────────────────
        now = datetime.now(timezone.utc)
        sample_users = [
            User(
                name="Sara Ahmed",
                email="sara@example.com",
                phone="01012345678",
                password_hash=hash_password("password123"),
                created_at=now - timedelta(days=14),
            ),
            User(
                name="Nour Hassan",
                email="nour@example.com",
                phone="01098765432",
                password_hash=hash_password("password123"),
                created_at=now - timedelta(days=12),
            ),
            User(
                name="Layla Ibrahim",
                email="layla@example.com",
                phone="01111111111",
                password_hash=hash_password("password123"),
                created_at=now - timedelta(days=10),
            ),
            User(
                name="Mariam Khaled",
                email="mariam@example.com",
                phone="01222222222",
                password_hash=hash_password("password123"),
                created_at=now - timedelta(days=7),
            ),
            User(
                name="Fatma Ali",
                email="fatma@example.com",
                phone="01333333333",
                password_hash=hash_password("password123"),
                created_at=now - timedelta(days=5),
            ),
            User(
                name="Hana Mohamed",
                email="hana@example.com",
                phone="01444444444",
                password_hash=hash_password("password123"),
                created_at=now - timedelta(days=3),
            ),
            User(
                name="Dina Samir",
                email="dina@example.com",
                phone="01555555555",
                password_hash=hash_password("password123"),
                created_at=now - timedelta(days=2),
            ),
            User(
                name="Rania Tarek",
                email="rania@example.com",
                phone="01666666666",
                password_hash=hash_password("password123"),
                created_at=now - timedelta(days=1),
            ),
        ]
        db.session.add_all(sample_users)
        db.session.flush()  # Get user IDs
        print("[+] 1 admin + 8 sample users seeded.")

        # ── 4. Sample Orders ─────────────────────────────────────────────
        sample_orders = [
            Order(user_id=sample_users[0].id, ticket_type_id=1, card_last_four="1234", created_at=now - timedelta(days=14)),
            Order(user_id=sample_users[1].id, ticket_type_id=2, card_last_four="5678", created_at=now - timedelta(days=12)),
            Order(user_id=sample_users[2].id, ticket_type_id=1, card_last_four="9012", created_at=now - timedelta(days=10)),
            Order(user_id=sample_users[3].id, ticket_type_id=3, card_last_four="3456", created_at=now - timedelta(days=7)),
            Order(user_id=sample_users[4].id, ticket_type_id=1, card_last_four="7890", created_at=now - timedelta(days=5)),
            Order(user_id=sample_users[5].id, ticket_type_id=2, card_last_four="2345", created_at=now - timedelta(days=3)),
            Order(user_id=sample_users[6].id, ticket_type_id=1, card_last_four="6789", created_at=now - timedelta(days=2)),
            Order(user_id=sample_users[7].id, ticket_type_id=2, card_last_four="0123", created_at=now - timedelta(days=1)),
        ]
        db.session.add_all(sample_orders)
        print("[+] 8 sample orders seeded.")

        # ── 5. Speakers (all 20 from original prototype) ─────────────────
        speakers_data = [
            # Featured speakers (shown on homepage)
            ("Salah Abo Elmagd", "CEO of ACTA and founder of TMS", True),
            ("Hesham Afifi", "Director", True),
            ("Eslam Hossam", "Creative Director", True),
            ("Amr Salama", "Filmmaker | Writer", True),
            ("Youssef Othman", "Actor - Content creator", True),
            ("Khaled Halfawy", "Film / TV Director", True),
            ("Waleed Khalil", "Managing Partner at Den VC", True),
            ("Islam El-Tiar", "CVM Director at WaffarX", True),
            # Non-featured speakers (all speakers page only)
            ("Jessy Radwan", "Founder and CEO Carerha", False),
            ("Omar El Aawar", "Founder & CEO Youth Summit", False),
            ("Omar Abdelsalam", "Founder & CEO POV", False),
            ("Yasmine Yehia", "Founder The Coaching Lab", False),
            ("Marianne Georges", "Business consultant", False),
            ("Marwa Abbas", "General Manager - IBM", False),
            ("Amll Askar", "Founder and CEO of Arise", False),
            ("Safaa Badr", "Skills and Learning Sr. Manager", False),
            ("Mai Zahra", "Sr. Employer Branding Partner", False),
            ("Omnia Kelig", "Deputy CEO - NAEEM Holding", False),
            ("Hilda Louca", "Founder & CEO, Mitcha", False),
            ("Eng. Ayman Elgohary", "Chairman of the Board, GSS", False),
        ]
        for i, (name, title, featured) in enumerate(speakers_data):
            db.session.add(
                Speaker(name=name, title=title, is_featured=featured, sort_order=i)
            )
        print("[+] 20 speakers seeded.")

        # ── 6. Sponsors (all from original prototype) ────────────────────
        sponsors_data = [
            # Diamond tier
            ("VOIS", "diamond", 0),
            ("Mashreq Bank", "diamond", 1),
            # Gold tier
            ("CIB", "gold", 0),
            ("SWVL", "gold", 1),
            ("WEN", "gold", 2),
            ("El Abd Foods", "gold", 3),
            ("Nogoum FM", "gold", 4),
            ("NCW", "gold", 5),
            ("Baheya Foundation", "gold", 6),
            # Silver tier
            ("Nola", "silver", 0),
            ("Eva Care", "silver", 1),
            ("Eva Cosmetics", "silver", 2),
            ("EFE Egypt", "silver", 3),
            ("ABS", "silver", 4),
            ("ITI", "silver", 5),
            ("ALX Arabia", "silver", 6),
            ("Nawy", "silver", 7),
            ("Egyptian Red Crescent", "silver", 8),
            ("MedSpark", "silver", 9),
            ("Abdaa", "silver", 10),
        ]
        for name, tier, order in sponsors_data:
            db.session.add(Sponsor(name=name, tier=tier, sort_order=order))
        print("[+] 20 sponsors seeded.")

        # ── 7. Agenda Items (all from original prototype) ────────────────
        agenda_data = [
            ("8:30 AM", "9:00 AM", "Registration", "Career180 Team", "main", 0),
            ("9:00 AM", "9:15 AM", "Opening Remarks", "Shrouk Alaa Eldin", "main", 1),
            (
                "9:30 AM",
                "10:15 AM",
                "Technology at Scale: Lessons from Global Tech Giants",
                "Moheb Halem, Dr. Amr Fahmy, Ahmed El-Bossati",
                "secondary",
                2,
            ),
            (
                "10:15 AM",
                "11:00 AM",
                "Inside the Deal Room: What Actually Happens Before a Startup Gets Funded?",
                "Amira Swilam, Hossam Shafick, Dr. Ahmed Abdelhamid",
                "main",
                3,
            ),
            (
                "11:00 AM",
                "11:45 AM",
                "She Took the Lead: Stories of Egypt's Most Powerful Women",
                "Hilda Louca, Ahella El Saban, Dalia Ibrahim, Omnia Kelig",
                "workshop",
                4,
            ),
            (
                "12:30 PM",
                "2:15 PM",
                "The Edge You Didn't Know You Had: Emotional Skills",
                "Mourad Abbas, Ayman Rizk, Yasmine Yehia",
                "secondary",
                5,
            ),
            (
                "4:15 PM",
                "5:00 PM",
                "Influence with Intent: Creators Changing the Narrative",
                "Raouf El Sherif, Hana Waleed Ghoneim, Moujeeb Elrahman",
                "main",
                6,
            ),
        ]
        for start, end, title, speakers_txt, stage, order in agenda_data:
            db.session.add(
                AgendaItem(
                    time_start=start,
                    time_end=end,
                    title=title,
                    speakers_text=speakers_txt,
                    stage=stage,
                    sort_order=order,
                )
            )
        print("[+] 7 agenda items seeded.")

        # ── Commit everything ────────────────────────────────────────────
        db.session.commit()
        print("\n[✓] Database seeded successfully!")
        print("    Admin login: admin@momken.com / admin123")


if __name__ == "__main__":
    seed()
