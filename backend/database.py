import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read Amazon RDS connection string from environment variable
# PostgreSQL RDS: postgresql+psycopg2://<DB_USER>:<DB_PASS>@<RDS_ENDPOINT>:5432/<DB_NAME>
# MySQL RDS     : mysql+pymysql://<DB_USER>:<DB_PASS>@<RDS_ENDPOINT>:3306/<DB_NAME>
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True  # Automatically reconnect if RDS connection drops
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
