# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func




class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120))
    email = Column(String(200))
    phone = Column(String(50))
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    is_admin = Column(Boolean, default=False)  
    quotes = relationship("Quote", back_populates="user")



class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(50))
    service = Column(String(100))
    details = Column(Text)  # ✅ ajout ici
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="quotes")
