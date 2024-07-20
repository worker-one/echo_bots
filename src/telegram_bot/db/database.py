from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Message, Base, User
import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    logger.error("DATABASE_URL is not set in the environment variables.")
    exit(1)
    
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def create_tables():
    Base.metadata.create_all(engine)

def log_message(user_id, message_text):
    session = Session()
    new_message = Message(
        timestamp=datetime.datetime.now(),
        user_id=user_id,
        message_text=message_text
    )
    session.add(new_message)
    session.commit()


def add_user(user_id, first_name, last_name, username, phone_number):
    session = Session()
    new_user = User(
        user_id=user_id,
        first_message_timestamp=datetime.datetime.now(),
        first_name=first_name,
        last_name=last_name,
        username=username,
        phone_number=phone_number
    )
    # add only if the user is not already in the database
    if not session.query(User).filter(User.user_id == user_id).first():
        session.add(new_user)
    session.commit()
