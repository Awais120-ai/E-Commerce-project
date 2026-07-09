from app.database import SessionLocal
from app import crud

session = SessionLocal()
users = crud.get_users(session)
for u in users:
    print(u.id, u.email, u.password)
session.close()
