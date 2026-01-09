import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import command
from models import Base

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def get_alembic_config(self):
#     config = Config()
#     config.set_main_option("script_location", "alembic")
#     config.set_main_option("sqlalchemy.url", DATABASE_URL)
#     return config
    
# def create_revision(self, message: str, autogenerate: bool = True):
#     config = self.get_alembic_config()
#     command.revision(config, autogenerate=autogenerate, message=message)
    
# def migrate_up(self, revision: str = "head"):
#    config = self.get_alembic_config()
#    command.upgrade(config, revision)

def get_db():
    dbsession = SessionLocal()
    try:
        yield dbsession
    finally:
        dbsession.close()


