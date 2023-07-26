from typing import List
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pydantic import BaseModel

# Replace 'sqlite:///event_registration.db' with your preferred database URL
DATABASE_URL = "sqlite:///event_registration.db"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    phone_number = Column(String, index=True)
    email = Column(String, index=True)
    residence = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)


class EventRegistrationCreate(BaseModel):
    full_name: str
    phone_number: str
    email: str
    residence: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register/", response_model=EventRegistrationCreate)
def register_for_event(event_registration: EventRegistrationCreate, db: Session = Depends(get_db)):
    db_event_registration = EventRegistration(**event_registration.dict())
    db.add(db_event_registration)
    db.commit()
    db.refresh(db_event_registration)
    return db_event_registration


@app.get("/registrations/", response_model=List[EventRegistrationCreate])
def get_event_registrations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(EventRegistration).offset(skip).limit(limit).all()
