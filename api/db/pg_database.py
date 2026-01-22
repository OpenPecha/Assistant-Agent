from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from api.config import get


engine = create_engine(get("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()