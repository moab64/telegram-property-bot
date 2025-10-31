from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Text, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

class UserFilter(Base):
    __tablename__ = "user_filters"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    city = Column(String(50), default="sari")
    property_type = Column(String(50))
    min_price = Column(BigInteger)
    max_price = Column(BigInteger)
    min_area = Column(Integer)
    max_area = Column(Integer)
    bedrooms = Column(Integer)
    advertiser_type = Column(String(20))  # owner, agent
    include_keywords = Column(Text)
    exclude_keywords = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Advertisement(Base):
    __tablename__ = "advertisements"
    
    id = Column(Integer, primary_key=True)
    source = Column(String(20), nullable=False)  # divar, sheypoor
    external_id = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    price = Column(BigInteger)
    area = Column(Integer)
    bedrooms = Column(Integer)
    property_type = Column(String(50))
    city = Column(String(50))
    district = Column(String(100))
    advertiser_type = Column(String(20))
    url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=func.now())
    seen_by_users = Column(JSON, default=[])  # List of user_ids who have seen this ad

class SentAd(Base):
    __tablename__ = "sent_ads"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    ad_id = Column(Integer, nullable=False)
    sent_at = Column(DateTime, default=func.now())