import os
import json
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import gspread
from google.oauth2.service_account import Credentials

from steps import WELCOME_TEXT, REMINDER_TEXT, MAIN_VIDEO_FILE_ID, auto_funnel
from config import BOT_TOKEN, OWNER_USERNAME, GOOGLE_SHEET_ID

# === Логгирование ===
logging.basicConfig(level=logging.INFO)

# === Google Sheets ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Загружаем креды из переменной окружения
credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
if not credentials_json:
    raise ValueError("Переменная GOOGLE_CREDENTIALS_JSON не задана")

creds = Credentials.from_service_account_info(json.loads(credentials_json), scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1

def log_to_sheet(user_id, username, event, action):
    try:
        sheet.append_row([str(user_id), username or "", event, str(datetime.now()), action])
    except Exception as e:
        logging.error(f"Ошибка записи в Google Таблицу: {e}")

# === FSM состояния ===
class UserState(StatesGroup):
    waiting_for_video_click = State()
    in_auto_funnel = State()

# === Инициализация бота ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
scheduler = AsyncIOScheduler()

def btn(text):
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=text)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# === HTTP-сервер для Render ===
app = Flask(__name__)

@app.route("/health")
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# === Обработчики бота ===

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username

    log_to_sheet(user_id, username, "start", "started")
    await state.set_state(UserState.waiting_for_video_click)
    await message.answer(WELCOME_TEXT, reply_markup=btn("Смотреть видео"))

    # Напоминание через 10 минут
    scheduler.add_job(
        send_pre_video_reminder,
        "date",
        run_date=datetime.now() + timedelta(minutes=10),
        args=[user_id],
        id=f"pre_reminder_{user_id}",
        replace_existing=True
    )

async def send_pre_video_reminder(user_id: int):
    try:
        await bot.send_message(user_id, REMINDER_TEXT, reply_markup=btn("Смотреть видео"))
        log_to_sheet(user_id, None, "pre_video_reminder", "sent")
    except Exception as e:
        logging.error(f"Не отправилось напоминание: {e}")

@dp.message(UserState.waiting_for_video_click)
async def handle_watch_video(message: types.Message, state: FSMContext):
    if message.text != "Смотреть видео":
        return

    user_id = message.from_user.id
    try:
        scheduler.remove_job(f"pre_reminder_{user_id}")
    except:
        pass

    log_to_sheet(user_id, None, "main_video_requested", "clicked")
    await message.answer_video(
        video=MAIN_VIDEO_FILE_ID,
        caption="Это видео — начало твоего эксперимента с настоящим отдыхом 💛",
        reply_markup=btn("Записаться")
    )

    await state.set_state(UserState.in_auto_funnel)
    log_to_sheet(user_id, None, "main_video_sent", "sent")

    # Запускаем автоматическую воронку
    for step in auto_funnel:
        run_time = datetime.now() + timedelta(minutes=step["delay_minutes_after_video"])
        scheduler.add_job(
            send_auto_step,
            "date",
            run_date=run_time,
            args=[user_id, step],
            id=f"auto_{user_id}_{step['description']}",
            replace_existing=True
        )

async def send_auto_step(user_id: int, step: dict):
    try:
        if step["type"] == "text":
            await bot.send_message(user_id, step["content"], reply_markup=btn("Записаться"))
        elif step["type"] == "audio":
            await bot.send_audio(user_id, audio=step["file_id"], reply_markup=btn("Записаться"))
        elif step["type"] == "document":
            await bot.send_document(user_id, document=step["file_id"], reply_markup=btn("Записаться"))
        elif step["type"] == "photo":
            await bot.send_photo(
                user_id,
                photo=step["file_id"],
                caption=step.get("caption", ""),
                reply_markup=btn("Записаться")
            )
        log_to_sheet(user_id, None, step["description"], "auto_sent")
    except Exception as e:
        logging.error(f"Ошибка авто-шага: {e}")

@dp.message(UserState.in_auto_funnel)
async def handle_signup(message: types.Message, state: FSMContext):
    if message.text != "Записаться":
        return

    user_id = message.from_user.id
    for step in auto_funnel:
        try:
            scheduler.remove_job(f"auto_{user_id}_{step['description']}")
        except:
            pass

    log_to_sheet(user_id, None, "manual_signup", "signed_up")
    url = f"https://t.me/{OWNER_USERNAME}?start=хочу_записаться_на_ретрит"
    await message.answer(
        "Спасибо! 💛 Сейчас перенаправлю тебя в личные сообщения — там можно уточнить детали.",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="👉 Написать организатору", url=url)]]
        )
    )
    await state.clear()

# === Запуск ===
async def run_bot():
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запускаем Flask в фоне
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаем бота
    asyncio.run(run_bot())
