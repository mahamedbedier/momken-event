import random
from app import create_app, db
from models import User

app = create_app()

cities = ["Cairo", "Alexandria", "Giza", "Mansoura", "Assiut", "Tanta"]
unis = ["Cairo University", "Ain Shams University", "AUC", "GUC", "Alexandria University"]
status = ["1st Year", "2nd Year", "3rd Year", "4th Year", "Fresh Graduate", "Working Professional"]
sources = ["Social Media", "Friends", "University", "Employer"]
goals = ["Job Opportunities", "AI Workshops", "Networking", "Startups", "Mentorship", "Certifications"]

with app.app_context():
    users = User.query.all()
    for u in users:
        # Don't overwrite if they actually have data
        if not u.city:
            u.city = random.choice(cities)
        if not u.university:
            u.university = random.choice(unis)
        if not u.academic_status:
            u.academic_status = random.choice(status)
        if not u.source:
            u.source = random.choice(sources)
        if not u.why_attending:
            u.why_attending = ", ".join(random.sample(goals, random.randint(1, 3)))
            
    db.session.commit()
    print("Seed data for demographics generated successfully!")
