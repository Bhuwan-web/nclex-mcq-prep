from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mcq_api.models import Base
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
print("Base directory:", BASE_DIR)
DATABASE_URL = "sqlite:///" + os.path.abspath(
    os.path.join(BASE_DIR, "../data_loader/nclex_simple.db")
)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
