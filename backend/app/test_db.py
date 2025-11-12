from sqlalchemy import create_engine, text

# Replace with your actual connection URL
engine = create_engine("postgresql+psycopg2://agrisense_user:abcde@localhost:5432/agrisense_db")

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Database connection successful:", result.scalar())
