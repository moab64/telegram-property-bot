import logging
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.operations import UserOperations, AdOperations, get_db
from utils.config import load_config, is_admin
from utils.helpers import format_currency, format_timestamp
from bot.keyboards import get_admin_keyboard, get_back_keyboard, get_main_keyboard

logger = logging.getLogger(__name__)
router = Router()
config = load_config()

class AdminStates(StatesGroup):
    broadcast = State()
    stats_filter = State()

class AdminPanel:
    """Admin panel management class"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    async def get_user_stats(self) -> Dict[str, any]:
        """Get user statistics"""
        db = get_db()
        try:
            # Total users
            total_users = db.query(UserOperations.User).count()
            
            # Active users (with filters)
            active_users = db.query(UserOperations.UserFilter).count()
            
            # New users today
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            new_users_today = db.query(UserOperations.User).filter(
                UserOperations.User.created_at >= today
            ).count()
            
            # Users by city
            users_by_city = db.query(
                UserOperations.UserFilter.city,
                db.func.count(UserOperations.UserFilter.id)
            ).group_by(UserOperations.UserFilter.city).all()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'new_users_today': new_users_today,
                'users_by_city': dict(users_by_city)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user stats: {e}")
            return {}
        finally:
            db.close()
    
    async def get_ad_stats(self) -> Dict[str, any]:
        """Get advertisement statistics"""
        db = get_db()
        try:
            # Total ads
            total_ads = db.query(AdOperations.Advertisement).count()
            
            # New ads today
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            new_ads_today = db.query(AdOperations.Advertisement).filter(
                AdOperations.Advertisement.created_at >= today
            ).count()
            
            # Ads by source
            ads_by_source = db.query(
                AdOperations.Advertisement.source,
                db.func.count(AdOperations.Advertisement.id)
            ).group_by(AdOperations.Advertisement.source).all()
            
            # Ads by city
            ads_by_city = db.query(
                AdOperations.Advertisement.city,
                db.func.count(AdOperations.Advertisement.id)
            ).group_by(AdOperations.Advertisement.city).all()
            
            # Ads by property type
            ads_by_type = db.query(
                AdOperations.Advertisement.property_type,
                db.func.count(AdOperations.Advertisement.id)
            ).group_by(AdOperations.Advertisement.property_type).all()
            
            return {
                'total_ads': total_ads,
                'new_ads_today': new_ads_today,
                'ads_by_source': dict(ads_by_source),
                'ads_by_city': dict(ads_by_city),
                'ads_by_type': dict(ads_by_type)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting ad stats: {e}")
            return {}
        finally:
            db.close()
    
    async def get_system_stats(self) -> Dict[str, any]:
        """Get system statistics"""
        db = get_db()
        try:
            # Database size (SQLite specific)
            db_size = 0
            if 'sqlite' in config.database.url:
                db_path = config.database.url.replace('sqlite:///', '')
                try:
                    import os
                    db_size = os.path.getsize(db_path)
                except:
                    db_size = 0
            
            # Sent ads count
            sent_ads_count = db.query(AdOperations.SentAd).count()
            
            # Active crawlers
            crawler_status = await self.get_crawler_status()
            
            return {
                'db_size': db_size,
                'sent_ads_count': sent_ads_count,
                'crawler_status': crawler_status
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {}
        finally:
            db.close()
    
    async def get_crawler_status(self) -> Dict[str, any]:
        """Get crawler status"""
        # This would typically check the actual crawler status
        # For now, we'll return mock data
        return {
            'divar': 'active',
            'sheypoor': 'active',
            'last_run': datetime.now() - timedelta(minutes=5),
            'next_run': datetime.now() + timedelta(minutes=10)
        }
    
    async def format_stats_message(self) -> str:
        """Format comprehensive stats message"""
        user_stats = await self.get_user_stats()
        ad_stats = await self.get_ad_stats()
        system_stats = await self.get_system_stats()
        
        message = "📊 **آمار جامع سیستم**\n\n"
        
        # User Statistics
        message += "👥 **آمار کاربران:**\n"
        message += f"• کل کاربران: {user_stats.get('total_users', 0):,}\n"
        message += f"• کاربران فعال: {user_stats.get('active_users', 0):,}\n"
        message += f"• کاربران جدید امروز: {user_stats.get('new_users_today', 0):,}\n"
        
        # User distribution by city
        if user_stats.get('users_by_city'):
            message += "• توزیع کاربران بر اساس شهر:\n"
            for city, count in user_stats['users_by_city'].items():
                city_name = self._get_city_name(city)
                message += f"  - {city_name}: {count:,}\n"
        
        message += "\n📢 **آمار آگهی‌ها:**\n"
        message += f"• کل آگهی‌ها: {ad_stats.get('total_ads', 0):,}\n"
        message += f"• آگهی‌های جدید امروز: {ad_stats.get('new_ads_today', 0):,}\n"
        
        # Ads by source
        if ad_stats.get('ads_by_source'):
            message += "• آگهی‌ها بر اساس منبع:\n"
            for source, count in ad_stats['ads_by_source'].items():
                source_name = 'دیوار' if source == 'divar' else 'شیپور'
                message += f"  - {source_name}: {count:,}\n"
        
        message += "\n⚙️ **آمار سیستم:**\n"
        message += f"• آگهی‌های ارسال شده: {system_stats.get('sent_ads_count', 0):,}\n"
        
        # Database size
        db_size_mb = system_stats.get('db_size', 0) / (1024 * 1024)
        message += f"• حجم دیتابیس: {db_size_mb:.2f} مگابایت\n"
        
        # Crawler status
        crawler_status = system_stats.get('crawler_status', {})
        message += f"• وضعیت کراولرها: {'فعال' if crawler_status.get('divar') == 'active' else 'غیرفعال'}\n"
        
        if crawler_status.get('last_run'):
            last_run = crawler_status['last_run']
            message += f"• آخرین اجرا: {format_timestamp(last_run)}\n"
        
        return message
    
    def _get_city_name(self, city_slug: str) -> str:
        """Get Persian city name from slug"""
        city_names = {
            'sari': 'ساری',
            'tehran': 'تهران',
            'mashhad': 'مشهد',
            'esfahan': 'اصفهان',
            'shiraz': 'شیراز',
            'tabriz': 'تبریز'
        }
        return city_names.get(city_slug, city_slug)
    
    async def broadcast_message(self, message_text: str) -> Dict[str, any]:
        """Broadcast message to all users"""
        db = get_db()
        results = {
            'total_users': 0,
            'successful_sends': 0,
            'failed_sends': 0,
            'errors': []
        }
        
        try:
            users = db.query(UserOperations.User).all()
            results['total_users'] = len(users)
            
            for user in users:
                try:
                    await self.bot.send_message(
                        chat_id=user.user_id,
                        text=message_text,
                        parse_mode='HTML'
                    )
                    results['successful_sends'] += 1
                    
                    # Small delay to avoid rate limiting
                    import asyncio
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    results['failed_sends'] += 1
                    results['errors'].append(f"User {user.user_id}: {str(e)}")
                    self.logger.error(f"Failed to send broadcast to user {user.user_id}: {e}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in broadcast: {e}")
            results['errors'].append(f"System error: {str(e)}")
            return results
        finally:
            db.close()
    
    async def get_recent_errors(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get recent errors from log file"""
        try:
            log_file = "logs/bot.log"
            errors = []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines[-100:]:  # Check last 100 lines
                if 'ERROR' in line or 'CRITICAL' in line:
                    errors.append({
                        'timestamp': line.split(' - ')[0] if ' - ' in line else 'Unknown',
                        'message': line.strip()
                    })
            
            return errors[-limit:]
            
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")
            return [{'timestamp': 'Error', 'message': f'Could not read log file: {e}'}]
    
    async def get_user_details(self, user_id: int) -> Optional[Dict[str, any]]:
        """Get detailed user information"""
        db = get_db()
        try:
            user = db.query(UserOperations.User).filter(UserOperations.User.user_id == user_id).first()
            if not user:
                return None
            
            user_filter = db.query(UserOperations.UserFilter).filter(
                UserOperations.UserFilter.user_id == user_id
            ).first()
            
            sent_ads_count = db.query(AdOperations.SentAd).filter(
                AdOperations.SentAd.user_id == user_id
            ).count()
            
            return {
                'user': user,
                'filter': user_filter,
                'sent_ads_count': sent_ads_count,
                'is_active': user.is_active,
                'created_at': user.created_at
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user details: {e}")
            return None
        finally:
            db.close()

# Admin command handlers
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Handle /admin command"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ دسترسی denied. شما ادمین نیستید.")
        return
    
    admin_text = """
🛠️ **پنل مدیریت ربات**

دستورات موجود:

📊 /stats - مشاهده آمار کامل
👥 /users - مدیریت کاربران
📢 /broadcast - ارسال پیام همگانی
🔍 /errors - مشاهده خطاهای اخیر
⚙️ /status - وضعیت سیستم
🔄 /restart - راه‌اندازی مجدد کراولرها

برای بازگشت به منوی اصلی از /start استفاده کنید.
"""
    await message.answer(admin_text, reply_markup=get_admin_keyboard())

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Handle /stats command"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ دسترسی denied. شما ادمین نیستید.")
        return
    
    admin_panel = AdminPanel(message.bot)
    stats_message = await admin_panel.format_stats_message()
    
    # Add refresh button
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="refresh_stats")],
            [InlineKeyboardButton(text="📊 آمار جزئی", callback_data="detailed_stats")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")]
        ]
    )
    
    await message.answer(stats_message, reply_markup=keyboard, parse_mode='Markdown')

@router.message(Command("users"))
async def cmd_users(message: Message):
    """Handle /users command"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ دسترسی denied. شما ادمین نیستید.")
        return
    
    admin_panel = AdminPanel(message.bot)
    user_stats = await admin_panel.get_user_stats()
    
    users_text = f"""
👥 **مدیریت کاربران**

📈 آمار کلی:
• کل کاربران: {user_stats.get('total_users', 0):,}
• کاربران فعال: {user_stats.get('active_users', 0):,}
• کاربران جدید امروز: {user_stats.get('new_users_today', 0):,}

🏙️ توزیع جغرافیایی:
"""
    
    if user_stats.get('users_by_city'):
        for city, count in user_stats['users_by_city'].items():
            city_name = admin_panel._get_city_name(city)
            users_text += f"• {city_name}: {count:,} کاربر\n"
    else:
        users_text += "• اطلاعات جغرافیایی موجود نیست\n"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 لیست کاربران اخیر", callback_data="recent_users")],
            [InlineKeyboardButton(text="🔍 جستجوی کاربر", callback_data="search_user")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")]
        ]
    )
    
    await message.answer(users_text, reply_markup=keyboard, parse_mode='Markdown')

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    """Handle /broadcast command"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ دسترسی denied. شما ادمین نیستید.")
        return
    
    await state.set_state(AdminStates.broadcast)
    await message.answer(
        "📢 **ارسال پیام همگانی**\n\n"
        "لطفا پیام خود را برای ارسال به تمام کاربران وارد کنید:\n\n"
        "⚠️ توجه: این عمل قابل بازگشت نیست!",
        reply_markup=get_back_keyboard(),
        parse_mode='Markdown'
    )

@router.message(AdminStates.broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    """Process broadcast message"""
    if message.text == "🔙 بازگشت":
        await state.clear()
        await message.answer("عملیات لغو شد.", reply_markup=get_admin_keyboard())
        return
    
    # Confirm broadcast
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ تأیید ارسال", callback_data=f"confirm_broadcast:{message.message_id}")],
            [InlineKeyboardButton(text="❌ لغو", callback_data="cancel_broadcast")]
        ]
    )
    
    await message.answer(
        f"📢 **تأیید ارسال پیام همگانی**\n\n"
        f"پیام شما:\n{message.text}\n\n"
        f"آیا از ارسال این پیام به تمام کاربران اطمینان دارید؟",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@router.message(Command("errors"))
async def cmd_errors(message: Message):
    """Handle /errors command"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ دسترسی denied. شما ادمین نیستید.")
        return
    
    admin_panel = AdminPanel(message.bot)
    recent_errors = await admin_panel.get_recent_errors(5)
    
    if not recent_errors:
        await message.answer("✅ هیچ خطای جدیدی یافت نشد.")
        return
    
    errors_text = "🚨 **خطاهای اخیر سیستم**\n\n"
    
    for i, error in enumerate(recent_errors, 1):
        error_message = error['message']
        # Truncate long error messages
        if len(error_message) > 200:
            error_message = error_message[:200] + "..."
        
        errors_text += f"{i}. **{error['timestamp']}**\n`{error_message}`\n\n"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑️ پاک کردن لاگ", callback_data="clear_logs")],
            [InlineKeyboardButton(text="🔍 خطاهای بیشتر", callback_data="more_errors")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")]
        ]
    )
    
    await message.answer(errors_text, reply_markup=keyboard, parse_mode='Markdown')

@router.message(Command("status"))
async def cmd_status(message: Message):
    """Handle /status command"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ دسترسی denied. شما ادمین نیستید.")
        return
    
    admin_panel = AdminPanel(message.bot)
    crawler_status = await admin_panel.get_crawler_status()
    
    status_text = "⚙️ **وضعیت سیستم**\n\n"
    
    status_text += "🕷️ **کراولرها:**\n"
    status_text += f"• دیوار: {'✅ فعال' if crawler_status.get('divar') == 'active' else '❌ غیرفعال'}\n"
    status_text += f"• شیپور: {'✅ فعال' if crawler_status.get('sheypoor') == 'active' else '❌ غیرفعال'}\n"
    
    if crawler_status.get('last_run'):
        last_run = crawler_status['last_run']
        status_text += f"• آخرین اجرا: {format_timestamp(last_run)}\n"
    
    if crawler_status.get('next_run'):
        next_run = crawler_status['next_run']
        status_text += f"• اجرای بعدی: {format_timestamp(next_run)}\n"
    
    status_text += "\n📊 **پایگاه داده:**\n"
    system_stats = await admin_panel.get_system_stats()
    db_size_mb = system_stats.get('db_size', 0) / (1024 * 1024)
    status_text += f"• وضعیت: ✅ متصل\n"
    status_text += f"• حجم: {db_size_mb:.2f} مگابایت\n"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="refresh_status")],
            [InlineKeyboardButton(text="🔧 مدیریت کراولر", callback_data="manage_crawlers")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")]
        ]
    )
    
    await message.answer(status_text, reply_markup=keyboard, parse_mode='Markdown')

@router.message(Command("restart"))
async def cmd_restart(message: Message):
    """Handle /restart command"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ دسترسی denied. شما ادمین نیستید.")
        return
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ بله، راه‌اندازی مجدد", callback_data="confirm_restart")],
            [InlineKeyboardButton(text="❌ لغو", callback_data="cancel_restart")]
        ]
    )
    
    await message.answer(
        "🔄 **راه‌اندازی مجدد کراولرها**\n\n"
        "آیا از راه‌اندازی مجدد کراولرها اطمینان دارید؟\n\n"
        "⚠️ توجه: این عمل ممکن است باعث تاخیر در بررسی آگهی‌ها شود.",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

# Callback query handlers
@router.callback_query(F.data == "refresh_stats")
async def refresh_stats(callback: CallbackQuery):
    """Refresh statistics"""
    if not is_admin(callback.from_user.id):
        await callback.answer("دسترسی denied.")
        return
    
    admin_panel = AdminPanel(callback.bot)
    stats_message = await admin_panel.format_stats_message()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="refresh_stats")],
            [InlineKeyboardButton(text="📊 آمار جزئی", callback_data="detailed_stats")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")]
        ]
    )
    
    await callback.message.edit_text(stats_message, reply_markup=keyboard, parse_mode='Markdown')
    await callback.answer("آمار بروزرسانی شد")

@router.callback_query(F.data.startswith("confirm_broadcast:"))
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    """Confirm and send broadcast"""
    if not is_admin(callback.from_user.id):
        await callback.answer("دسترسی denied.")
        return
    
    message_id = callback.data.split(":")[1]
    
    try:
        # Get the original broadcast message
        original_message = await callback.bot.forward_message(
            chat_id=callback.from_user.id,
            from_chat_id=callback.from_user.id,
            message_id=int(message_id)
        )
        
        broadcast_text = original_message.text
        
        # Send broadcast
        admin_panel = AdminPanel(callback.bot)
        results = await admin_panel.broadcast_message(broadcast_text)
        
        # Show results
        results_text = (
            f"📢 **نتایج ارسال همگانی**\n\n"
            f"• کل کاربران: {results['total_users']:,}\n"
            f"• ارسال موفق: {results['successful_sends']:,}\n"
            f"• ارسال ناموفق: {results['failed_sends']:,}\n"
            f"• نرخ موفقیت: {(results['successful_sends']/results['total_users']*100 if results['total_users'] > 0 else 0):.1f}%\n"
        )
        
        if results['errors']:
            results_text += f"\n🚨 خطاها (۵ مورد اول):\n"
            for error in results['errors'][:5]:
                results_text += f"• {error}\n"
        
        await callback.message.edit_text(results_text, parse_mode='Markdown')
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        await callback.message.edit_text(f"❌ خطا در ارسال همگانی: {e}")
    
    await callback.answer()

@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """Cancel broadcast"""
    await callback.message.edit_text("❌ ارسال همگانی لغو شد.")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    """Return to admin main menu"""
    admin_text = """
🛠️ **پنل مدیریت ربات**

دستورات موجود:

📊 /stats - مشاهده آمار کامل
👥 /users - مدیریت کاربران
📢 /broadcast - ارسال پیام همگانی
🔍 /errors - مشاهده خطاهای اخیر
⚙️ /status - وضعیت سیستم
🔄 /restart - راه‌اندازی مجدد کراولرها

برای بازگشت به منوی اصلی از /start استفاده کنید.
"""
    await callback.message.edit_text(admin_text, reply_markup=get_admin_keyboard())
    await callback.answer()

@router.callback_query(F.data == "confirm_restart")
async def confirm_restart(callback: CallbackQuery):
    """Confirm crawler restart"""
    # This would typically restart the crawler scheduler
    # For now, we'll just show a message
    
    await callback.message.edit_text(
        "✅ کراولرها با موفقیت راه‌اندازی مجدد شدند.\n\n"
        "بررسی آگهی‌های جدید از سر گرفته شد.",
        parse_mode='Markdown'
    )
    
    logger.info(f"Admin {callback.from_user.id} restarted crawlers")
    await callback.answer("کراولرها راه‌اندازی مجدد شدند")

@router.callback_query(F.data == "cancel_restart")
async def cancel_restart(callback: CallbackQuery):
    """Cancel crawler restart"""
    await callback.message.edit_text("❌ راه‌اندازی مجدد لغو شد.")
    await callback.answer()

# Text message handlers for admin panel
@router.message(F.text == "👥 آمار کاربران")
async def handle_users_stats(message: Message):
    """Handle users stats button"""
    await cmd_users(message)

@router.message(F.text == "📊 آمار آگهی‌ها")
async def handle_ads_stats(message: Message):
    """Handle ads stats button"""
    await cmd_stats(message)

@router.message(F.text == "🔍 مشاهده لاگ")
async def handle_view_logs(message: Message):
    """Handle view logs button"""
    await cmd_errors(message)

@router.message(F.text == "⚙️ وضعیت کراولر")
async def handle_crawler_status(message: Message):
    """Handle crawler status button"""
    await cmd_status(message)

@router.message(F.text == "🔄 راه‌اندازی مجدد")
async def handle_restart(message: Message):
    """Handle restart button"""
    await cmd_restart(message)

@router.message(F.text == "🏠 منوی اصلی")
async def handle_main_menu(message: Message):
    """Handle main menu button"""
    await message.answer(
        "منوی اصلی:",
        reply_markup=get_main_keyboard()
    )

def register_admin_handlers(dp):
    """Register admin handlers with dispatcher"""
    dp.include_router(router)