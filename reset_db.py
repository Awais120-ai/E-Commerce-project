from app.database import engine, Base

# Drop all tables
Base.metadata.drop_all(bind=engine)
# Recreate tables
Base.metadata.create_all(bind=engine)
print('Database reset complete.')
