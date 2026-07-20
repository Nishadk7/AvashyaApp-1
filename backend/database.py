import os
import urllib.parse
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

# Environment variables for RDS IAM Authentication or Standard Connection URL
RDSHOST = os.getenv("RDSHOST")
DBUSER = os.getenv("DBUSER", "nishad")
DBNAME = os.getenv("DBNAME", "postgres")
DBPORT = int(os.getenv("DBPORT", "5432"))
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

DATABASE_URL = os.getenv("DATABASE_URL")

connect_args = {}

if RDSHOST:
    # -------------------------------------------------------------------------
    # AWS IAM Database Authentication Pattern
    # Generates dynamic IAM auth tokens using boto3
    # -------------------------------------------------------------------------
    try:
        import boto3
        rds_client = boto3.client("rds", region_name=AWS_REGION)
        raw_token = rds_client.generate_db_auth_token(
            DBHostname=RDSHOST,
            Port=DBPORT,
            DBUsername=DBUSER,
            Region=AWS_REGION
        )
        encoded_token = urllib.parse.quote_plus(raw_token)
        DATABASE_URL = f"postgresql+psycopg2://{DBUSER}:{encoded_token}@{RDSHOST}:{DBPORT}/{DBNAME}?sslmode=require"
        logger.info(f"Connected to RDS PostgreSQL using AWS IAM DB Auth (Host: {RDSHOST}, User: {DBUSER})")
    except Exception as e:
        logger.error(f"Failed to generate IAM DB Auth token: {e}")
        if not DATABASE_URL:
            DATABASE_URL = "sqlite:///./app.db"

elif not DATABASE_URL:
    DATABASE_URL = "sqlite:///./app.db"

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
