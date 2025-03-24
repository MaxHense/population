import os

from sqlmodel import create_engine
from app.logger import logger

def check_database_connection() -> bool:
    '''
    Check if the database connection is successful
    '''
    db_url = os.getenv('DBURL')
    engine = create_engine(db_url, echo=False)

    logger.info("Checking database connection")
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error("Database connection failed")
        return False