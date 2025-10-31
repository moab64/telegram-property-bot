def update_user_filter(user_id: int, filter_data: dict):
    """به‌روزرسانی فیلتر کاربر - ساده‌شده برای فقط شهر"""
    try:
        user_filter = session.query(UserFilter).filter_by(user_id=user_id).first()
        
        if not user_filter:
            user_filter = UserFilter(user_id=user_id)
            session.add(user_filter)
        
        # فقط شهر الزامی است، بقیه می‌توانند None باشند
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
        
        session.commit()
        return user_filter
        
    except Exception as e:
        logger.error(f"Error updating user filter: {e}")
        session.rollback()
        return None
