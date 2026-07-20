import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

RDSHOST = os.getenv("RDSHOST")
DBUSER = os.getenv("DBUSER", "nishad")
DBNAME = os.getenv("DBNAME", "postgres")
DBPORT = int(os.getenv("DBPORT", "5432"))
DBPASSWORD = os.getenv("DBPASSWORD")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

DATABASE_URL = os.getenv("DATABASE_URL")

connect_args = {}

if RDSHOST:
    import psycopg2
    import boto3

    def get_rds_connection():
        if DBPASSWORD:
            return psycopg2.connect(
                host=RDSHOST,
                port=DBPORT,
                database=DBNAME,
                user=DBUSER,
                password=DBPASSWORD,
                sslmode='require'
            )
        else:
            rds_client = boto3.client('rds', region_name=AWS_REGION)
            auth_token = rds_client.generate_db_auth_token(
                DBHostname=RDSHOST,
                Port=DBPORT,
                DBUsername=DBUSER,
                Region=AWS_REGION
            )
            return psycopg2.connect(
                host=RDSHOST,
                port=DBPORT,
                database=DBNAME,
                user=DBUSER,
                password=auth_token,
                sslmode='require'
            )

    engine = create_engine(
        'postgresql+psycopg2://',
        creator=get_rds_connection,
        pool_pre_ping=True
    )

elif DATABASE_URL:
    if DATABASE_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True
    )
else:
    DATABASE_URL = "sqlite:///./app.db"
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
