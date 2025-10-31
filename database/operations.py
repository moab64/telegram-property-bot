from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

from .models import Base, User, UserFilter, Advertisement, SentAd
from utils.config import load_config

logger = logging.getLogger(__name__)
config = load_config()

engine = create_engine(config.database.url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {e}")

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

class UserOperations:
    @staticmethod
    def get_or_create_user(user_id, username=None, first_name=None, last_name=None):
        db = get_db()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            return user
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error getting/creating user: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def get_user_filter(user_id):
        db = get_db()
        try:
            return db.query(UserFilter).filter(UserFilter.user_id == user_id).first()
        finally:
            db.close()

    @staticmethod
    def update_user_filter(user_id, filter_data):
        db = get_db()
        try:
            user_filter = db.query(UserFilter).filter(UserFilter.user_id == user_id).first()
            if user_filter:
                for key, value in filter_data.items():
                    setattr(user_filter, key, value)
            else:
                user_filter = UserFilter(user_id=user_id, **filter_data)
                db.add(user_filter)
            db.commit()
            return user_filter
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating user filter: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def reset_user_filter(user_id):
        db = get_db()
        try:
            user_filter = db.query(UserFilter).filter(UserFilter.user_id == user_id).first()
            if user_filter:
                db.delete(user_filter)
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error resetting user filter: {e}")
            return False
        finally:
            db.close()

class AdOperations:
    @staticmethod
    def ad_exists(source, external_id):
        db = get_db()
        try:
            return db.query(Advertisement).filter(
                Advertisement.source == source,
                Advertisement.external_id == external_id
            ).first() is not None
        finally:
            db.close()

    @staticmethod
    def create_ad(ad_data):
        db = get_db()
        try:
            ad = Advertisement(**ad_data)
            db.add(ad)
            db.commit()
            db.refresh(ad)
            return ad
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating ad: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def mark_ad_sent(user_id, ad_id):
        db = get_db()
        try:
            sent_ad = SentAd(user_id=user_id, ad_id=ad_id)
            db.add(sent_ad)
            
            # Update seen_by_users in Advertisement
            ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
            if ad and user_id not in ad.seen_by_users:
                ad.seen_by_users.append(user_id)
            
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error marking ad as sent: {e}")
        finally:
            db.close()

    @staticmethod
    def get_unsent_ads_for_user(user_id, user_filter):
        db = get_db()
        try:
            query = db.query(Advertisement).filter(
                ~Advertisement.seen_by_users.any(user_id)
            )
            
            # Apply filters
            if user_filter.city:
                query = query.filter(Advertisement.city == user_filter.city)
            if user_filter.property_type:
                query = query.filter(Advertisement.property_type == user_filter.property_type)
            if user_filter.min_price:
                query = query.filter(Advertisement.price >= user_filter.min_price)
            if user_filter.max_price:
                query = query.filter(Advertisement.price <= user_filter.max_price)
            if user_filter.min_area:
                query = query.filter(Advertisement.area >= user_filter.min_area)
            if user_filter.max_area:
                query = query.filter(Advertisement.area <= user_filter.max_area)
            if user_filter.bedrooms:
                query = query.filter(Advertisement.bedrooms == user_filter.bedrooms)
            if user_filter.advertiser_type:
                query = query.filter(Advertisement.advertiser_type == user_filter.advertiser_type)
            
            return query.order_by(Advertisement.created_at.desc()).all()
        finally:
            db.close()