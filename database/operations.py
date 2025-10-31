import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

logger = logging.getLogger(__name__)

# ایجاد پایگاه داده
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class UserFilter(Base):
    __tablename__ = 'user_filters'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    city = Column(String(100))
    property_type = Column(String(100))
    min_price = Column(Integer)
    max_price = Column(Integer)
    min_area = Column(Integer)
    max_area = Column(Integer)
    bedrooms = Column(Integer)
    advertiser_type = Column(String(100))
    include_keywords = Column(Text)
    exclude_keywords = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# اتصال به دیتابیس SQLite
engine = create_engine('sqlite:///bot_database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class UserOperations:
    
    @staticmethod
    def get_or_create_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """دریافت یا ایجاد کاربر جدید"""
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                session.commit()
                logger.info(f"User created: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error in get_or_create_user: {e}")
            session.rollback()
            return None
    
    @staticmethod
    def get_user_filter(user_id: int):
        """دریافت فیلترهای کاربر"""
        try:
            return session.query(UserFilter).filter_by(user_id=user_id).first()
        except Exception as e:
            logger.error(f"Error getting user filter: {e}")
            return None
    
    @staticmethod
    def update_user_filter(user_id: int, filter_data: dict):
        """به‌روزرسانی فیلتر کاربر"""
        try:
            user_filter = session.query(UserFilter).filter_by(user_id=user_id).first()
            
            if not user_filter:
                user_filter = UserFilter(user_id=user_id)
                session.add(user_filter)
            
            # به‌روزرسانی فیلدها
            user_filter.city = filter_data.get('city')
            user_filter.property_type = filter_data.get('property_type')
            user_filter.min_price = filter_data.get('min_price')
            user_filter.max_price = filter_data.get('max_price')
            user_filter.min_area = filter_data.get('min_area')
            user_filter.max_area = filter_data.get('max_area')
            user_filter.bedrooms = filter_data.get('bedrooms')
            user_filter.advertiser_type = filter_data.get('advertiser_type')
            user_filter.include_keywords = filter_data.get('include_keywords')
            user_filter.exclude_keywords = filter_data.get('exclude_keywords')
            user_filter.updated_at = datetime.utcnow()
            
            session.commit()
            logger.info(f"Filter updated for user: {user_id}")
            return user_filter
            
        except Exception as e:
            logger.error(f"Error updating user filter: {e}")
            session.rollback()
            return None
    
    @staticmethod
    def reset_user_filter(user_id: int):
        """حذف فیلترهای کاربر"""
        try:
            user_filter = session.query(UserFilter).filter_by(user_id=user_id).first()
            if user_filter:
                session.delete(user_filter)
                session.commit()
                logger.info(f"Filter reset for user: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resetting user filter: {e}")
            session.rollback()
            return False
