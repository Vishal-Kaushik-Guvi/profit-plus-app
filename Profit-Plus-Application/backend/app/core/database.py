from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create the database engine (connection pool)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# Each request gets its own session (like EntityManager in JPA)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All models will extend this Base class
Base = declarative_base()
