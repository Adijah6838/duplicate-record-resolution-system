from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    address = Column(String)
    date_of_birth = Column(Date, nullable=True)
    status = Column(String, default="active")  # active | merged | rejected
    merged_into_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class DuplicateCandidate(Base):
    __tablename__ = "duplicate_candidates"
    id = Column(Integer, primary_key=True, index=True)
    customer_a_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    customer_b_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    score = Column(Float, nullable=False)
    name_score = Column(Float, default=0)
    email_score = Column(Float, default=0)
    phone_score = Column(Float, default=0)
    address_score = Column(Float, default=0)
    dob_score = Column(Float, default=0)
    decision = Column(String, default="pending")  # pending | approved | rejected
    created_at = Column(DateTime, server_default=func.now())

class MergeHistory(Base):
    __tablename__ = "merge_history"
    id = Column(Integer, primary_key=True, index=True)
    survivor_id = Column(Integer, nullable=False)
    merged_id = Column(Integer, nullable=False)
    score = Column(Float)
    action = Column(String)  # merged | rejected
    created_at = Column(DateTime, server_default=func.now())
