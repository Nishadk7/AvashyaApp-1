import os
import logging
import psycopg2
import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

RDSHOST = os.getenv("RDSHOST", "avashya-db-instance-instance-1.czoekaswcg9j.ap-south-1.rds.amazonaws.com")
DBUSER = os.getenv("DBUSER", "nishad")
DBNAME = os.getenv("DBNAME", "postgres")
DBPORT = int(os.getenv("DBPORT", "5432"))
DBPASSWORD = os.getenv("DBPASSWORD")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
