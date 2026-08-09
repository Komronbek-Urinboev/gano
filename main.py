#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from l import TEXTS
import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from contextlib import asynccontextmanager
from io import BytesIO
from collections import defaultdict

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton,
    WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton,
    ContentType, BufferedInputFile, ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter, TelegramNetworkError

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Text, BigInteger, ForeignKey, inspect
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.sql import func
from sqlalchemy import text

import pandas as pd
from dotenv import load_dotenv

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== ANTI-SPAM CONFIG ====================
class AntiSpam:
    def __init__(self):
        self.user_messages = defaultdict(list)
        self.blocked_users = {}
        self.max_messages = 7  # Максимум сообщений
        self.time_window = 5  # За 5 секунд
        self.block_duration = 15  # Блокировка на 15 секунд

    def is_spam(self, user_id: int) -> bool:
        """Проверяет, является ли действие спамом"""
        now = datetime.now()

        # Проверяем, не заблокирован ли пользователь
        if user_id in self.blocked_users:
            if now < self.blocked_users[user_id]:
                return True
            else:
                del self.blocked_users[user_id]
                self.user_messages[user_id].clear()

        # Очищаем старые сообщения
        self.user_messages[user_id] = [
            msg_time for msg_time in self.user_messages[user_id]
            if now - msg_time < timedelta(seconds=self.time_window)
        ]

        # Добавляем текущее сообщение
        self.user_messages[user_id].append(now)

        # Проверяем лимит
        if len(self.user_messages[user_id]) > self.max_messages:
            self.blocked_users[user_id] = now + timedelta(seconds=self.block_duration)
            logger.warning(f"User {user_id} blocked for spam (antiflood)")
            return True

        return False

    def is_limited(self, user_id: int) -> bool:
        """Проверяет, превышен ли лимит (без блокировки)"""
        now = datetime.now()

        if user_id in self.blocked_users:
            if now < self.blocked_users[user_id]:
                return True
            else:
                del self.blocked_users[user_id]
                self.user_messages[user_id].clear()
                return False

        self.user_messages[user_id] = [
            msg_time for msg_time in self.user_messages[user_id]
            if now - msg_time < timedelta(seconds=self.time_window)
        ]

        return len(self.user_messages[user_id]) >= self.max_messages


anti_spam = AntiSpam()

# ==================== LOAD PRODUCTS ====================
try:
    with open("products.json", "r", encoding="utf-8") as f:
        PRODUCTS_CATALOG = {p["id"]: p for p in json.load(f)}
    logger.info(f"Loaded {len(PRODUCTS_CATALOG)} products from catalog")
except FileNotFoundError:
    logger.warning("products.json not found!")
    PRODUCTS_CATALOG = {}
except Exception as e:
    logger.error(f"Error loading products.json: {e}")
    PRODUCTS_CATALOG = {}

# ==================== CONFIG ====================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing")

try:
    ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
except ValueError:
    raise ValueError("ADMIN_TELEGRAM_ID must be an integer")

if ADMIN_TELEGRAM_ID == 0:
    raise ValueError("ADMIN_TELEGRAM_ID must be set and non-zero")

logger.info(f"Admin ID: {ADMIN_TELEGRAM_ID}")

WEBAPP_URL = os.getenv("WEBAPP_URL", "https://komronbek-urinboev.github.io/gano/")
DATABASE_URL = "sqlite:///gano_shop.db"

ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.heic', '.pdf')

# ==================== MULTILANGUAGE DICTIONARY ====================
TEXTS = {
    'uz': {
        'welcome': '👋 *Gano Excel* do\'koniga xush kelibsiz!\n\n🌿 Tabiiy Ganoderma asosidagi premium mahsulotlar',
        'open_store': '🛍 Do\'konni ochish',
        'my_orders': '📋 Mening buyurtmalarim',
        'help': '❓ Yordam',
        'about': 'ℹ️ Biz haqimizda',
        'language': '🌐 Til',
        'back_to_menu': '🔙 Asosiy menyuga',
        'lang_choice': '🌐 Tilni tanlang / Выберите язык / Choose language:',
        'lang_changed': '✅ Til o\'zgartirildi!',
        'order_summary': '📋 *Buyurtmangiz:*\n\n{items}\n\n💰 *Jami:* {total} so\'m\n\nDavom ettirishni xohlaysizmi?',
        'continue_order': '✅ Davom ettirish',
        'cancel_order': '❌ Bekor qilish',
        'order_cancelled_by_user': '❌ Buyurtma bekor qilindi.',
        'ask_contact': '📞 Iltimos, telefon raqamingizni yuboring:',
        'ask_location': '📍 Iltimos, geolokatsiyangizni yuboring yoki qo\'lda kiriting:',
        'ask_address': '📝 To\'liq manzilingizni yozing:\nMasalan: Toshkent, Mirzo Ulug\'bek tumani, 5-mavze, 12-uy',
        'ask_landmarks': '🏢 Mo\'ljal olish uchun qo\'shimcha ma\'lumot bering (ixtiyoriy):\nMasalan: "Supermarket yonida" yoki "Maktab ro\'parasida"',
        'payment_instructions': '💳 *To\'lov:* \n\nIltimos, {total} so\'mni quyidagi kartaga o\'tkazing:\n\n`1234 5678 9012 3456`\n\nTo\'lov chekini yuboring:',
        'receipt_success': '✅ *Buyurtma qabul qilindi!*\n\nAdmin tez orada buyurtmangizni tasdiqlaydi.',
        'receipt_invalid': '❌ Iltimos, rasm yoki PDF formatidagi to\'lov chekini yuboring.',
        'error_general': '❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.',
        'spam_warning': '⚠️ Juda ko\'p so\'rov yubordingiz. Iltimos, 15 soniya kuting.',
        'my_orders_empty': '📭 Hali hech qanday buyurtma yo\'q.',
        'my_orders_title': '📋 *Sizning buyurtmalaringiz:*\n\n',
        'help_text': '💬 Agar savollaringiz bo\'lsa, admin bilan bog\'laning:',
        'about_text': '🌿 *Gano Excel*\n\nBiz Ganoderma Lucidum asosidagi premium mahsulotlarni taklif qilamiz.\n\nSifat va tabiiylik — bizning asosiy tamoyilimiz.',
        'admin_panel': '🔧 *Admin paneli*',
        'admin_export_users': '👥 Foydalanuvchilarni export qilish',
        'admin_order_stats': '📊 Statistika',
        'admin_broadcast': '📢 Xabar yuborish',
        'admin_new_order': '🆕 *Yangi buyurtma #{order_id}*\n\n👤 {name} (ID: {user_id})\n📞 {phone}\n\n📦 *Mahsulotlar:*\n{items}\n\n💰 *Jami:* {total} so\'m\n📍 *Lokatsiya:* {loc}\n📝 *Manzil:* {addr}\n🏢 *Mo\'ljal:* {landmarks}',
        'admin_map_links': '📍 Manzilni xaritada ochish:',
        'admin_confirm': '✅ Buyurtma tasdiqlandi',
        'admin_cancel': '❌ Buyurtma bekor qilindi',
        'order_confirmed_by_admin': '✅ Buyurtmangiz tasdiqlandi! Tez orada yetkazib beramiz.',
        'order_cancelled_by_admin': '❌ Buyurtmangiz bekor qilindi.',
        'admin_broadcast_instruction': '📢 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:',
        'admin_broadcast_sent': '✅ Xabar {count} foydalanuvchiga yuborildi.',
        'admin_broadcast_cancelled': '❌ Jo\'natish bekor qilindi.',
        'admin_stats': '📊 *Statistika*\n\n✅ Tasdiqlangan: {confirmed}\n❌ Bekor qilingan: {cancelled}',
    },
    'ru': {
        'welcome': '👋 Добро пожаловать в магазин *Gano Excel*!\n\n🌿 Премиум продукты на основе Ganoderma',
        'open_store': '🛍 Открыть магазин',
        'my_orders': '📋 Мои заказы',
        'help': '❓ Помощь',
        'about': 'ℹ️ О нас',
        'language': '🌐 Язык',
        'back_to_menu': '🔙 В главное меню',
        'lang_choice': '🌐 Tilni tanlang / Выберите язык / Choose language:',
        'lang_changed': '✅ Язык изменён!',
        'order_summary': '📋 *Ваш заказ:*\n\n{items}\n\n💰 *Итого:* {total} сум\n\nПродолжить оформление?',
        'continue_order': '✅ Продолжить',
        'cancel_order': '❌ Отменить',
        'order_cancelled_by_user': '❌ Заказ отменён.',
        'ask_contact': '📞 Пожалуйста, отправьте ваш номер телефона:',
        'ask_location': '📍 Пожалуйста, отправьте вашу геолокацию или укажите адрес вручную:',
        'ask_address': '📝 Напишите ваш полный адрес:\nНапример: Ташкент, Мирзо-Улугбекский район, 5-й квартал, дом 12',
        'ask_landmarks': '🏢 Укажите ориентиры (необязательно):\nНапример: "Рядом с супермаркетом" или "Напротив школы"',
        'payment_instructions': '💳 *Оплата:* \n\nПожалуйста, переведите {total} сум на карту:\n\n`1234 5678 9012 3456`\n\nОтправьте чек об оплате:',
        'receipt_success': '✅ *Заказ принят!*\n\nАдминистратор скоро подтвердит ваш заказ.',
        'receipt_invalid': '❌ Пожалуйста, отправьте чек в формате фото или PDF.',
        'error_general': '❌ Произошла ошибка. Пожалуйста, попробуйте снова.',
        'spam_warning': '⚠️ Слишком много запросов. Пожалуйста, подождите 15 секунд.',
        'my_orders_empty': '📭 У вас пока нет заказов.',
        'my_orders_title': '📋 *Ваши заказы:*\n\n',
        'help_text': '💬 Если у вас есть вопросы, свяжитесь с администратором:',
        'about_text': '🌿 *Gano Excel*\n\nМы предлагаем премиум продукты на основе Ganoderma Lucidum.\n\nКачество и натуральность — наш главный принцип.',
        'admin_panel': '🔧 *Панель администратора*',
        'admin_export_users': '👥 Экспорт пользователей',
        'admin_order_stats': '📊 Статистика',
        'admin_broadcast': '📢 Рассылка',
        'admin_new_order': '🆕 *Новый заказ #{order_id}*\n\n👤 {name} (ID: {user_id})\n📞 {phone}\n\n📦 *Товары:*\n{items}\n\n💰 *Итого:* {total} сум\n📍 *Локация:* {loc}\n📝 *Адрес:* {addr}\n🏢 *Ориентиры:* {landmarks}',
        'admin_map_links': '📍 Открыть адрес на карте:',
        'admin_confirm': '✅ Заказ подтверждён',
        'admin_cancel': '❌ Заказ отменён',
        'order_confirmed_by_admin': '✅ Ваш заказ подтверждён! Скоро доставим.',
        'order_cancelled_by_admin': '❌ Ваш заказ отменён.',
        'admin_broadcast_instruction': '📢 Напишите сообщение для рассылки всем пользователям:',
        'admin_broadcast_sent': '✅ Сообщение отправлено {count} пользователям.',
        'admin_broadcast_cancelled': '❌ Рассылка отменена.',
        'admin_stats': '📊 *Статистика*\n\n✅ Подтверждено: {confirmed}\n❌ Отменено: {cancelled}',
    },
    'en': {
        'welcome': '👋 Welcome to *Gano Excel* store!\n\n🌿 Premium products based on Ganoderma',
        'open_store': '🛍 Open Store',
        'my_orders': '📋 My Orders',
        'help': '❓ Help',
        'about': 'ℹ️ About Us',
        'language': '🌐 Language',
        'back_to_menu': '🔙 Main Menu',
        'lang_choice': '🌐 Tilni tanlang / Выберите язык / Choose language:',
        'lang_changed': '✅ Language changed!',
        'order_summary': '📋 *Your Order:*\n\n{items}\n\n💰 *Total:* {total} UZS\n\nProceed with checkout?',
        'continue_order': '✅ Continue',
        'cancel_order': '❌ Cancel',
        'order_cancelled_by_user': '❌ Order cancelled.',
        'ask_contact': '📞 Please send your phone number:',
        'ask_location': '📍 Please send your location or enter address manually:',
        'ask_address': '📝 Write your full address:\nExample: Tashkent, Mirzo-Ulugbek district, 5th block, 12',
        'ask_landmarks': '🏢 Provide landmarks (optional):\nExample: "Next to supermarket" or "Opposite school"',
        'payment_instructions': '💳 *Payment:* \n\nPlease transfer {total} UZS to card:\n\n`1234 5678 9012 3456`\n\nSend payment receipt:',
        'receipt_success': '✅ *Order accepted!*\n\nAdmin will confirm your order shortly.',
        'receipt_invalid': '❌ Please send a photo or PDF receipt.',
        'error_general': '❌ An error occurred. Please try again.',
        'spam_warning': '⚠️ Too many requests. Please wait 15 seconds.',
        'my_orders_empty': '📭 No orders yet.',
        'my_orders_title': '📋 *Your Orders:*\n\n',
        'help_text': '💬 If you have questions, contact admin:',
        'about_text': '🌿 *Gano Excel*\n\nWe offer premium Ganoderma Lucidum based products.\n\nQuality and naturalness — our main principle.',
        'admin_panel': '🔧 *Admin Panel*',
        'admin_export_users': '👥 Export Users',
        'admin_order_stats': '📊 Statistics',
        'admin_broadcast': '📢 Broadcast',
        'admin_new_order': '🆕 *New Order #{order_id}*\n\n👤 {name} (ID: {user_id})\n📞 {phone}\n\n📦 *Products:*\n{items}\n\n💰 *Total:* {total} UZS\n📍 *Location:* {loc}\n📝 *Address:* {addr}\n🏢 *Landmarks:* {landmarks}',
        'admin_map_links': '📍 Open address on map:',
        'admin_confirm': '✅ Order confirmed',
        'admin_cancel': '❌ Order cancelled',
        'order_confirmed_by_admin': '✅ Your order has been confirmed! We will deliver soon.',
        'order_cancelled_by_admin': '❌ Your order has been cancelled.',
        'admin_broadcast_instruction': '📢 Write a message to broadcast to all users:',
        'admin_broadcast_sent': '✅ Message sent to {count} users.',
        'admin_broadcast_cancelled': '❌ Broadcast cancelled.',
        'admin_stats': '📊 *Statistics*\n\n✅ Confirmed: {confirmed}\n❌ Cancelled: {cancelled}',
    }
}

# ==================== DATABASE MODELS ====================
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    language = Column(String(2), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(50), default="New")
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    address = relationship("Address", back_populates="order", uselist=False)
    payment = relationship("Payment", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address_text = Column(Text, nullable=False)
    landmarks = Column(Text, nullable=True)
    order = relationship("Order", back_populates="address")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    receipt_file_id = Column(String(255), nullable=True)
    receipt_type = Column(String(20), nullable=True)
    payment_status = Column(String(50), default="Pending")
    paid_at = Column(DateTime, nullable=True)
    order = relationship("Order", back_populates="payment")


# ==================== AUTO MIGRATION ====================
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)


def ensure_columns():
    with engine.connect() as conn:
        inspector = inspect(engine)
        if 'payments' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('payments')]
            if 'receipt_type' not in cols:
                conn.execute(text("ALTER TABLE payments ADD COLUMN receipt_type TEXT"))
                conn.commit()
                logger.info("Added receipt_type to payments")
        if 'users' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('users')]
            if 'language' not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR(2)"))
                conn.commit()
                logger.info("Added language to users")


Base.metadata.create_all(bind=engine)
ensure_columns()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== FSM STATES ====================
class CheckoutState(StatesGroup):
    waiting_contact = State()
    waiting_location = State()
    waiting_address = State()
    waiting_landmarks = State()
    waiting_receipt = State()


# ==================== BOT INIT ====================
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


# ==================== ERROR HANDLER (ИСПРАВЛЕНО ДЛЯ AIOGRAM 3.X) ====================
@dp.errors()
async def error_handler(event):
    """Глобальный обработчик ошибок для aiogram 3.x"""
    exception = event.exception
    logger.error(f"Unhandled exception: {exception}", exc_info=True)

    if isinstance(exception, TelegramRetryAfter):
        logger.warning(f"Rate limit exceeded. Sleeping for {exception.retry_after} seconds")
        await asyncio.sleep(exception.retry_after)
        return True

    if isinstance(exception, TelegramNetworkError):
        logger.error(f"Network error occurred: {exception}")
        await asyncio.sleep(1)
        return True

    # Не прерываем бота при любых ошибках
    return True


# ==================== HELPER FUNCTIONS ====================
async def safe_send_message(chat_id: int, text: str, **kwargs):
    """Безопасная отправка сообщения с retry логикой"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return await bot.send_message(chat_id, text, **kwargs)
        except TelegramRetryAfter as e:
            logger.warning(f"Rate limit hit, waiting {e.retry_after}s")
            await asyncio.sleep(e.retry_after)
        except TelegramAPIError as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to send message after {max_retries} attempts: {e}")
                return None
            await asyncio.sleep(1 * (attempt + 1))
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return None


async def get_user_lang(user_id: int) -> str:
    """Возвращает язык пользователя или 'en' по умолчанию"""
    db = next(get_db())
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        lang = user.language if user and user.language in TEXTS else None
        return lang if lang else 'en'
    finally:
        db.close()


async def set_user_lang(user_id: int, lang: str):
    db = next(get_db())
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            user.language = lang
            db.commit()
        else:
            user = User(telegram_id=user_id, language=lang)
            db.add(user)
            db.commit()
    finally:
        db.close()


def get_main_keyboard(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS[lang]['open_store']), KeyboardButton(text=TEXTS[lang]['my_orders'])],
            [KeyboardButton(text=TEXTS[lang]['help']), KeyboardButton(text=TEXTS[lang]['about'])],
            [KeyboardButton(text=TEXTS[lang]['language'])]
        ],
        resize_keyboard=True
    )


def get_store_keyboard(lang: str):
    web_app_button = KeyboardButton(text=TEXTS[lang]['open_store'], web_app=WebAppInfo(url=WEBAPP_URL))
    return ReplyKeyboardMarkup(keyboard=[[web_app_button]], resize_keyboard=True)


def get_contact_keyboard(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]['ask_contact'], request_contact=True)]],
        resize_keyboard=True
    )


def get_location_keyboard(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]['ask_location'], request_location=True)]],
        resize_keyboard=True
    )


def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")]
    ])


def get_admin_keyboard(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]['admin_export_users'], callback_data="admin_export_users")],
        [InlineKeyboardButton(text=TEXTS[lang]['admin_order_stats'], callback_data="admin_stats")],
        [InlineKeyboardButton(text=TEXTS[lang]['admin_broadcast'], callback_data="admin_broadcast")]
    ])


def get_admin_order_keyboard(user_id: int, lat: float, lon: float, lang: str):
    """Создает клавиатуру с картами и кнопками confirm/cancel"""
    keyboard = []

    # Кнопка чата
    keyboard.append([InlineKeyboardButton(text="💬 Open Chat", url=f"tg://user?id={user_id}")])

    # Кнопки карт
    maps_row = []
    if lat and lon:
        maps_row.append(InlineKeyboardButton(text="🗺️ Google Maps", url=f"https://www.google.com/maps?q={lat},{lon}"))
        maps_row.append(
            InlineKeyboardButton(text="🗺️ Yandex Maps", url=f"https://yandex.com/maps/?pt={lon},{lat}&z=15&l=map"))
        keyboard.append(maps_row)

        maps_row2 = []
        maps_row2.append(InlineKeyboardButton(text="🗺️ 2GIS", url=f"https://2gis.ru/geo/{lon},{lat}"))
        maps_row2.append(InlineKeyboardButton(text="🗺️ Apple Maps", url=f"http://maps.apple.com/?ll={lat},{lon}&z=15"))
        keyboard.append(maps_row2)

    # Кнопки confirm/cancel
    keyboard.append([
        InlineKeyboardButton(text="✅ Confirm", callback_data=f"admin_confirm_{user_id}"),
        InlineKeyboardButton(text="❌ Cancel", callback_data=f"admin_cancel_{user_id}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_order_keyboard_without_actions(user_id: int, lat: float, lon: float):
    """Создает клавиатуру без кнопок confirm/cancel (после действия админа)"""
    keyboard = []

    # Кнопка чата
    keyboard.append([InlineKeyboardButton(text="💬 Open Chat", url=f"tg://user?id={user_id}")])

    # Кнопки карт
    if lat and lon:
        maps_row = []
        maps_row.append(InlineKeyboardButton(text="🗺️ Google Maps", url=f"https://www.google.com/maps?q={lat},{lon}"))
        maps_row.append(
            InlineKeyboardButton(text="🗺️ Yandex Maps", url=f"https://yandex.com/maps/?pt={lon},{lat}&z=15&l=map"))
        keyboard.append(maps_row)

        maps_row2 = []
        maps_row2.append(InlineKeyboardButton(text="🗺️ 2GIS", url=f"https://2gis.ru/geo/{lon},{lat}"))
        maps_row2.append(InlineKeyboardButton(text="🗺️ Apple Maps", url=f"http://maps.apple.com/?ll={lat},{lon}&z=15"))
        keyboard.append(maps_row2)

    # Статус вместо кнопок действий
    keyboard.append([InlineKeyboardButton(text="✅ Processed", callback_data="admin_done")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ==================== DB HELPERS ====================
def get_or_create_user(db: Session, telegram_id: int, username: str = None, full_name: str = None):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, username=username, full_name=full_name, language=None)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if username and user.username != username:
            user.username = username
        if full_name and user.full_name != full_name:
            user.full_name = full_name
        db.commit()
    return user


def save_order(db: Session, user_id: int, order_data: Dict, contact: str, location: Dict,
               address_text: str, landmarks: str, receipt_file_id: str = None, receipt_type: str = None):
    order = Order(
        user_id=user_id,
        total_price=order_data["total_price"],
        status="New"
    )
    db.add(order)
    db.flush()

    for item in order_data["items"]:
        order_item = OrderItem(
            order_id=order.id,
            product_name=item["name"],
            quantity=item["quantity"],
            price=item["price"]
        )
        db.add(order_item)

    address = Address(
        order_id=order.id,
        latitude=location.get("latitude"),
        longitude=location.get("longitude"),
        address_text=address_text,
        landmarks=landmarks
    )
    db.add(address)

    payment = Payment(
        order_id=order.id,
        receipt_file_id=receipt_file_id,
        receipt_type=receipt_type,
        payment_status="Pending"
    )
    db.add(payment)

    user = db.query(User).filter(User.id == user_id).first()
    if user and not user.phone:
        user.phone = contact

    db.commit()
    return order.id


# ==================== NOTIFY ADMIN ====================
async def notify_admin(order_id: int, order_data: Dict, contact: str, location: Dict,
                       address_text: str, landmarks: str, receipt_file_id: str, receipt_type: str, user: User):
    lang = user.language if user.language in TEXTS else 'en'
    items_text = "\n".join([f"- {item['name']} x{item['quantity']} = {item['price'] * item['quantity']} so'm"
                            for item in order_data["items"]])
    lat = location.get('latitude')
    lon = location.get('longitude')
    loc_str = f"{lat}, {lon}" if lat and lon else "❌ not set"
    message_text = TEXTS[lang]['admin_new_order'].format(
        order_id=order_id,
        name=user.full_name or user.username,
        user_id=user.telegram_id,
        phone=contact,
        items=items_text,
        total=order_data["total_price"],
        loc=loc_str,
        addr=address_text,
        landmarks=landmarks or '-'
    )
    await safe_send_message(ADMIN_TELEGRAM_ID, message_text, parse_mode=ParseMode.MARKDOWN)

    if lat and lon:
        try:
            await bot.send_location(ADMIN_TELEGRAM_ID, latitude=lat, longitude=lon)
        except Exception as e:
            logger.error(f"Failed to send location: {e}")

    # Отправляем клавиатуру с картами и кнопками действий
    keyboard = get_admin_order_keyboard(user.telegram_id, lat, lon, lang)
    await safe_send_message(ADMIN_TELEGRAM_ID, TEXTS[lang]['admin_map_links'], reply_markup=keyboard)

    if receipt_file_id:
        try:
            if receipt_type == 'photo':
                await bot.send_photo(ADMIN_TELEGRAM_ID, receipt_file_id, caption="🧾 Receipt")
            else:
                await bot.send_document(ADMIN_TELEGRAM_ID, receipt_file_id, caption="🧾 Receipt")
        except Exception as e:
            logger.error(f"Failed to send receipt to admin: {e}")


# ==================== HANDLERS ====================
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    # Проверка на спам
    if anti_spam.is_spam(user_id):
        try:
            await message.answer(TEXTS[lang]['spam_warning'])
        except KeyError:
            await message.answer("⚠️ Too many requests. Please wait 15 seconds.")
        return

    db = next(get_db())
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        has_lang = user and user.language is not None

        if not has_lang:
            await message.answer(TEXTS['en']['lang_choice'], reply_markup=get_lang_keyboard())
            return

        await message.answer(TEXTS[lang]['welcome'], parse_mode=ParseMode.MARKDOWN,
                             reply_markup=get_main_keyboard(lang))
    finally:
        db.close()


@dp.message(Command("language"))
async def cmd_language(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(TEXTS['en']['lang_choice'], reply_markup=get_lang_keyboard())


@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await set_user_lang(callback.from_user.id, lang)
    await callback.message.delete()
    await callback.message.answer(TEXTS[lang]['welcome'], parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=get_main_keyboard(lang))
    await callback.answer(TEXTS[lang]['lang_changed'])


# ---------- Команда /admin ----------
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return
    lang = await get_user_lang(message.from_user.id)
    if not lang or lang not in TEXTS:
        lang = 'en'
    await message.answer(TEXTS[lang]['admin_panel'], parse_mode=ParseMode.MARKDOWN,
                         reply_markup=get_admin_keyboard(lang))
    logger.info(f"Admin panel shown to {message.from_user.id}")


# ---------- Общий хендлер для кнопок меню (только когда нет активного FSM) ----------
@dp.message(StateFilter(None), F.text)
async def handle_menu_buttons(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    # Проверка на спам (используем is_spam только для блокировки, не для предупреждения)
    if anti_spam.is_spam(user_id):
        try:
            await message.answer(TEXTS[lang]['spam_warning'])
        except KeyError:
            await message.answer("⚠️ Too many requests. Please wait 15 seconds.")
        return

    text = message.text
    if text == TEXTS[lang]['open_store']:
        await message.answer(TEXTS[lang]['open_store'], reply_markup=get_store_keyboard(lang))
    elif text == TEXTS[lang]['my_orders']:
        db = next(get_db())
        try:
            user = get_or_create_user(db, user_id, message.from_user.username, message.from_user.full_name)
            orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(10).all()
            if not orders:
                await message.answer(TEXTS[lang]['my_orders_empty'])
                return
            resp = TEXTS[lang]['my_orders_title']
            for order in orders:
                emoji = {"New": "🆕", "Confirmed": "✅", "Processing": "🔄", "Delivered": "🚚", "Cancelled": "❌"}.get(
                    order.status, "❓")
                resp += f"{emoji} #{order.id} — {order.created_at.strftime('%d.%m.%Y')} — {order.total_price} so'm — {order.status}\n"
            await message.answer(resp, parse_mode=ParseMode.MARKDOWN)
        finally:
            db.close()
    elif text == TEXTS[lang]['help']:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 Contact Admin", url="tg://resolve?domain=your_admin_username")]])
        await message.answer(TEXTS[lang]['help_text'], reply_markup=kb)
    elif text == TEXTS[lang]['about']:
        await message.answer(TEXTS[lang]['about_text'], parse_mode=ParseMode.MARKDOWN)
    elif text == TEXTS[lang]['language']:
        await message.answer(TEXTS[lang]['lang_choice'], reply_markup=get_lang_keyboard())
    elif text == TEXTS[lang]['back_to_menu']:
        await state.clear()
        await message.answer(TEXTS[lang]['back_to_menu'], reply_markup=get_main_keyboard(lang))


# ---------- WebApp data ----------
@dp.message(F.content_type == ContentType.WEB_APP_DATA)
async def handle_web_app_data(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)

    # Проверка на спам
    if anti_spam.is_spam(user_id):
        try:
            await message.answer(TEXTS[lang]['spam_warning'])
        except KeyError:
            await message.answer("⚠️ Too many requests. Please wait 15 seconds.")
        return

    try:
        raw_data = json.loads(message.web_app_data.data)
        logger.info(f"Received WebApp data from user {user_id}: {raw_data}")

        if not raw_data.get("items") or not isinstance(raw_data["items"], list):
            raise ValueError("Invalid items format")

        # Формируем безопасный order_data на стороне бэкенда
        bot_order_data = {"items": [], "total_price": 0}

        for item in raw_data["items"]:
            product_id = item.get("id")
            quantity = item.get("quantity", 1)

            # Ищем товар в нашем каталоге
            product_info = PRODUCTS_CATALOG.get(product_id)
            if not product_info:
                logger.warning(f"Product {product_id} not found in catalog!")
                continue

            price = product_info["price"]
            # Пытаемся взять имя на языке пользователя, иначе берем первое попавшееся
            name = product_info["name"].get(lang, list(product_info["name"].values())[0])

            bot_order_data["items"].append({
                "name": name,
                "price": price,
                "quantity": quantity
            })
            bot_order_data["total_price"] += price * quantity

        # Если корзина оказалась пустой после проверки
        if not bot_order_data["items"]:
            await message.answer(TEXTS[lang].get('error_general', 'Products not found.'))
            return

        await state.update_data(order_data=bot_order_data)
        await state.set_state(CheckoutState.waiting_contact)

        items_text = "\n".join(
            [f"{item['name']} x{item['quantity']} = {item['price'] * item['quantity']} so'm"
             for item in bot_order_data["items"]])
        summary = TEXTS[lang]['order_summary'].format(items=items_text, total=bot_order_data["total_price"])

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]['continue_order'], callback_data="confirm_order")],
            [InlineKeyboardButton(text=TEXTS[lang]['cancel_order'], callback_data="cancel_order")]
        ])
        await message.answer(summary, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

    except Exception as e:
        logger.error(f"WebApp error for user {user_id}: {e}", exc_info=True)
        await message.answer(TEXTS[lang].get('error_general', 'An error occurred.'))


# ---------- Callback handlers for order confirmation ----------
@dp.callback_query(F.data == "confirm_order", StateFilter(CheckoutState.waiting_contact))
async def confirm_order_callback(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(TEXTS[lang]['ask_contact'], reply_markup=get_contact_keyboard(lang))
    await state.set_state(CheckoutState.waiting_contact)
    await callback.answer()


@dp.callback_query(F.data == "cancel_order")
async def cancel_order_callback(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(callback.from_user.id)
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(TEXTS[lang]['order_cancelled_by_user'], reply_markup=get_main_keyboard(lang))
    await callback.answer()


# ---------- Contact ----------
@dp.message(StateFilter(CheckoutState.waiting_contact), F.contact)
async def receive_contact(message: Message, state: FSMContext):
    lang = await get_user_lang(message.from_user.id)
    await state.update_data(contact=message.contact.phone_number)
    await message.answer(TEXTS[lang]['ask_location'], reply_markup=get_location_keyboard(lang))
    await state.set_state(CheckoutState.waiting_location)


@dp.message(StateFilter(CheckoutState.waiting_contact))
async def wrong_contact(message: Message):
    lang = await get_user_lang(message.from_user.id)
    await message.answer(TEXTS[lang]['ask_contact'], reply_markup=get_contact_keyboard(lang))


# ---------- Location ----------
@dp.message(StateFilter(CheckoutState.waiting_location), F.location)
async def receive_location(message: Message, state: FSMContext):
    lang = await get_user_lang(message.from_user.id)
    lat, lon = message.location.latitude, message.location.longitude
    if abs(lat) < 0.0001 and abs(lon) < 0.0001:
        await message.answer(TEXTS[lang]['ask_location'], reply_markup=get_location_keyboard(lang))
        return
    await state.update_data(location={"latitude": lat, "longitude": lon})
    await message.answer(TEXTS[lang]['ask_address'], reply_markup=ReplyKeyboardRemove())
    await state.set_state(CheckoutState.waiting_address)


@dp.message(StateFilter(CheckoutState.waiting_location))
async def wrong_location(message: Message):
    lang = await get_user_lang(message.from_user.id)
    await message.answer(TEXTS[lang]['ask_location'], reply_markup=get_location_keyboard(lang))


# ---------- Address ----------
@dp.message(StateFilter(CheckoutState.waiting_address), F.text)
async def receive_address(message: Message, state: FSMContext):
    lang = await get_user_lang(message.from_user.id)
    addr = message.text.strip()
    if not addr:
        await message.answer(TEXTS[lang]['ask_address'])
        return
    await state.update_data(address_text=addr)
    await message.answer(TEXTS[lang]['ask_landmarks'], reply_markup=ReplyKeyboardRemove())
    await state.set_state(CheckoutState.waiting_landmarks)


@dp.message(StateFilter(CheckoutState.waiting_address))
async def wrong_address(message: Message):
    lang = await get_user_lang(message.from_user.id)
    await message.answer(TEXTS[lang]['ask_address'])


# ---------- Landmarks ----------
@dp.message(StateFilter(CheckoutState.waiting_landmarks))
async def receive_landmarks(message: Message, state: FSMContext):
    lang = await get_user_lang(message.from_user.id)
    landmarks = message.text.strip()
    if landmarks == "-":
        landmarks = ""
    await state.update_data(landmarks=landmarks)
    data = await state.get_data()
    total = data["order_data"]["total_price"]
    await message.answer(TEXTS[lang]['payment_instructions'].format(total=total), parse_mode=ParseMode.MARKDOWN,
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(CheckoutState.waiting_receipt)


# ---------- Receipt ----------
@dp.message(StateFilter(CheckoutState.waiting_receipt), F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT}))
async def receive_receipt(message: Message, state: FSMContext):
    lang = await get_user_lang(message.from_user.id)
    file_id = None
    receipt_type = None
    if message.photo:
        file_id = message.photo[-1].file_id
        receipt_type = 'photo'
    elif message.document:
        if not any(message.document.file_name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            await message.answer(TEXTS[lang]['receipt_invalid'])
            return
        file_id = message.document.file_id
        receipt_type = 'document'

    data = await state.get_data()
    order_data = data["order_data"]
    contact = data["contact"]
    location = data["location"]
    address_text = data["address_text"]
    landmarks = data.get("landmarks", "")

    db = next(get_db())
    try:
        user = get_or_create_user(db, message.from_user.id, message.from_user.username, message.from_user.full_name)
        order_id = save_order(db, user.id, order_data, contact, location, address_text, landmarks, file_id,
                              receipt_type)
    finally:
        db.close()

    await state.clear()
    await message.answer(TEXTS[lang]['receipt_success'], parse_mode=ParseMode.MARKDOWN,
                         reply_markup=get_main_keyboard(lang))
    await notify_admin(order_id, order_data, contact, location, address_text, landmarks, file_id, receipt_type, user)


@dp.message(StateFilter(CheckoutState.waiting_receipt))
async def wrong_receipt(message: Message):
    lang = await get_user_lang(message.from_user.id)
    await message.answer(TEXTS[lang]['receipt_invalid'])


# ---------- Admin callbacks ----------
@dp.callback_query(F.data == "admin_done")
async def admin_done(callback: CallbackQuery):
    """Заглушка для кнопки Processed"""
    await callback.answer("✅ Already processed")


@dp.callback_query(F.data == "admin_export_users")
async def admin_export_users(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_TELEGRAM_ID:
        await callback.answer("Access denied")
        return
    db = next(get_db())
    try:
        users = db.query(User).all()
        data = [{
            "ID": u.id, "Telegram ID": u.telegram_id, "Username": u.username,
            "Full Name": u.full_name, "Phone": u.phone, "Language": u.language,
            "Registered At": u.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for u in users]
    finally:
        db.close()

    df = pd.DataFrame(data)
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Users", index=False)
    out.seek(0)
    await callback.message.delete()
    await callback.message.answer_document(BufferedInputFile(out.getvalue(), filename="users.xlsx"))
    await callback.answer()


@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_TELEGRAM_ID:
        await callback.answer("Access denied")
        return
    db = next(get_db())
    try:
        confirmed = db.query(Order).filter(Order.status == "Confirmed").count()
        cancelled = db.query(Order).filter(Order.status == "Cancelled").count()
    finally:
        db.close()

    lang = await get_user_lang(callback.from_user.id)
    if not lang or lang not in TEXTS:
        lang = 'en'
    text = TEXTS[lang]['admin_stats'].format(confirmed=confirmed, cancelled=cancelled)
    await callback.message.delete()
    await callback.message.answer(text, parse_mode=ParseMode.MARKDOWN)
    await callback.answer()


@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_TELEGRAM_ID:
        await callback.answer("Access denied")
        return
    lang = await get_user_lang(callback.from_user.id)
    if not lang or lang not in TEXTS:
        lang = 'en'
    await state.set_state("broadcast")
    await callback.message.delete()
    await callback.message.answer(TEXTS[lang]['admin_broadcast_instruction'])
    await callback.answer()


@dp.message(StateFilter("broadcast"))
async def admin_broadcast_send(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return
    lang = await get_user_lang(message.from_user.id)
    if not lang or lang not in TEXTS:
        lang = 'en'
    if not message.text:
        await message.answer(TEXTS[lang]['admin_broadcast_instruction'])
        return
    db = next(get_db())
    try:
        users = db.query(User).all()
        count = 0
        for u in users:
            try:
                await safe_send_message(u.telegram_id, message.text)
                count += 1
                await asyncio.sleep(0.05)
            except Exception as e:
                logger.error(f"Broadcast failed to {u.telegram_id}: {e}")
    finally:
        db.close()

    await state.clear()
    await message.answer(TEXTS[lang]['admin_broadcast_sent'].format(count=count))


@dp.message(Command("cancel_broadcast"))
async def cancel_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_TELEGRAM_ID:
        return
    lang = await get_user_lang(message.from_user.id)
    if not lang or lang not in TEXTS:
        lang = 'en'
    await state.clear()
    await message.answer(TEXTS[lang]['admin_broadcast_cancelled'])


@dp.callback_query(F.data.startswith("admin_confirm_"))
async def admin_confirm_order(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_TELEGRAM_ID:
        await callback.answer("Access denied")
        return
    user_id = int(callback.data.split("_")[-1])
    db = next(get_db())
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            order = db.query(Order).filter(Order.user_id == user.id).order_by(Order.id.desc()).first()
            if order and order.status == "New":
                order.status = "Confirmed"
                db.commit()

                # Обновляем клавиатуру: убираем Confirm/Cancel, оставляем карты и чат
                lat = order.address.latitude if order.address else None
                lon = order.address.longitude if order.address else None
                new_keyboard = get_admin_order_keyboard_without_actions(user_id, lat, lon)
                await callback.message.edit_reply_markup(reply_markup=new_keyboard)

                lang = user.language if user.language in TEXTS else 'en'
                await safe_send_message(user.telegram_id, TEXTS[lang]['order_confirmed_by_admin'])
                await callback.answer("✅ Order confirmed!")
    finally:
        db.close()


@dp.callback_query(F.data.startswith("admin_cancel_"))
async def admin_cancel_order(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_TELEGRAM_ID:
        await callback.answer("Access denied")
        return
    user_id = int(callback.data.split("_")[-1])
    db = next(get_db())
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            order = db.query(Order).filter(Order.user_id == user.id).order_by(Order.id.desc()).first()
            if order and order.status == "New":
                order.status = "Cancelled"
                db.commit()

                # Обновляем клавиатуру: убираем Confirm/Cancel, оставляем карты и чат
                lat = order.address.latitude if order.address else None
                lon = order.address.longitude if order.address else None
                new_keyboard = get_admin_order_keyboard_without_actions(user_id, lat, lon)
                await callback.message.edit_reply_markup(reply_markup=new_keyboard)

                lang = user.language if user.language in TEXTS else 'en'
                await safe_send_message(user.telegram_id, TEXTS[lang]['order_cancelled_by_admin'])
                await callback.answer("❌ Order cancelled!")
    finally:
        db.close()


# ==================== FASTAPI ADMIN PANEL ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()


fastapi_app = FastAPI(title="Gano Shop Admin API", lifespan=lifespan)


@fastapi_app.get("/export/orders/excel")
async def export_orders_excel():
    db = next(get_db())
    try:
        orders = db.query(Order).order_by(Order.id).all()
        data = []
        for o in orders:
            user = o.user
            items = "\n".join([f"{i.product_name} x{i.quantity}" for i in o.items])
            addr = o.address.address_text if o.address else ""
            payment_status = o.payment.payment_status if o.payment else "Pending"
            data.append({
                "Order ID": o.id,
                "Username": user.username or "",
                "Phone": user.phone or "",
                "Products": items,
                "Total Price (UZS)": o.total_price,
                "Address": addr,
                "Payment Status": payment_status,
                "Status": o.status,
                "Created At": o.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
    finally:
        db.close()

    df = pd.DataFrame(data)
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Orders", index=False)
    out.seek(0)
    return StreamingResponse(out, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=orders.xlsx"})


# ==================== MAIN ====================
async def start_bot():
    logger.info("Starting bot polling...")
    while True:
        try:
            await dp.start_polling(bot, skip_updates=True)
        except Exception as e:
            logger.error(f"Bot polling failed: {e}", exc_info=True)
            await asyncio.sleep(5)


async def start_fastapi():
    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    while True:
        try:
            await asyncio.gather(start_bot(), start_fastapi())
        except Exception as e:
            logger.error(f"Main loop error: {e}", exc_info=True)
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)