from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.utils.config import settings
from app.utils.logger import logger

engine = create_engine(settings.MYSQL_URI, future=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    try:
        from app.db import models
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.exception('init_db failed: %s', e)