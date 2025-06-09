from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Change the path as needed
DB_PATH = 'installer.db'
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

# Usage:
# from db.session import init_db, Session
# init_db()  # Creates tables if not exist
# session = Session()
