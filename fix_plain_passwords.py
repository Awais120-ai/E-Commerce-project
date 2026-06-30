"""
One-time migration: re-hash any plain-text passwords left in the DB
by the update_user bug (now fixed in crud.py).

A bcrypt hash always starts with '$2b$' — any password that doesn't
is plain-text and needs to be re-hashed.

Run with:  python fix_plain_passwords.py
"""

from app.database import SessionLocal
from app.models.user import User
from app.utils.password import hash_password

db = SessionLocal()

try:
    users = db.query(User).all()
    fixed = 0

    for user in users:
        if not user.password.startswith("$2b$"):
            print(f"[FIX] User id={user.id} email={user.email} has plain-text password — re-hashing.")
            user.password = hash_password(user.password)
            fixed += 1

    if fixed:
        db.commit()
        print(f"\n✅ Fixed {fixed} user(s). They can now log in with their original password.")
    else:
        print("✅ No plain-text passwords found. All passwords are correctly hashed.")

finally:
    db.close()
