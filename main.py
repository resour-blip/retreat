import os
import json
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from flask import Flask
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import gspread
from google.oauth2.service_account import Credentials
from steps import WELCOME_MEDIA_FILE_ID, WELCOME_MEDIA_TYPE, REMINDER_TEXT, MAIN_VIDEO_FILE_ID, auto_funnel
from config import BOT_TOKEN, OWNER_USERNAME, GOOGLE_SHEET_ID

# === Логгирование ===
logging.basicConfig(level=logging.INFO)

# === Google Sheets ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
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

# === Inline-кнопка ===
def inline_btn(text: str, callback_data: str):
    return types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text=text, callback_data=callback_data)]]
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

    # Отправляем кружок (всегда, если WELCOME_MEDIA_TYPE == "video_note")
    if WELCOME_MEDIA_TYPE == "video_note":
        # await message.answer_video_note(video_note=WELCOME_MEDIA_FILE_ID)        
        await message.answer_video_note(video_note="DQACAgIAAxkBAAE9WfFpCN-Oeas6n1_Zl3F8QizFGS3XJQACrIgAAgLpSUiyyb8IyY5kEjYE")
        await message.answer(
            "🎥 Готов к эксперименту?",
            reply_markup=inline_btn("Смотреть видео", "watch_video")
        )
    elif WELCOME_MEDIA_TYPE == "video":
        await message.answer_video(
            video=WELCOME_MEDIA_FILE_ID,
            reply_markup=inline_btn("Смотреть видео", "watch_video")
        )
    elif WELCOME_MEDIA_TYPE == "photo":
        await message.answer_photo(
            photo=WELCOME_MEDIA_FILE_ID,
            reply_markup=inline_btn("Смотреть видео", "watch_video")
        )
    elif WELCOME_MEDIA_TYPE == "audio":
        await message.answer_audio(
            audio=WELCOME_MEDIA_FILE_ID,
            reply_markup=inline_btn("Смотреть видео", "watch_video")
        )
    else:
        await message.answer(
            "Привет! Готов к эксперименту?",
            reply_markup=inline_btn("Смотреть видео", "watch_video")
        )

    # Напоминание
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
        await bot.send_message(
            user_id,
            REMINDER_TEXT,
            reply_markup=inline_btn("Смотреть видео", "watch_video")
        )
        log_to_sheet(user_id, None, "pre_video_reminder", "sent")
    except Exception as e:
        logging.error(f"Не отправилось напоминание: {e}")

@dp.callback_query(F.data == "watch_video")
async def handle_watch_video(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id

    try:
        scheduler.remove_job(f"pre_reminder_{user_id}")
    except:
        pass

    log_to_sheet(user_id, None, "main_video_requested", "clicked")
    await callback.message.answer_video(
        video=MAIN_VIDEO_FILE_ID,
        caption="Это видео — начало твоего эксперимента с настоящим отдыхом 💛",
        reply_markup=inline_btn("Записаться", "signup")
    )
    await state.set_state(UserState.in_auto_funnel)
    log_to_sheet(user_id, None, "main_video_sent", "sent")

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
            await bot.send_message(
                user_id,
                step["content"],
                reply_markup=inline_btn("Записаться", "signup")
            )
        elif step["type"] == "audio":
            await bot.send_audio(
                user_id,
                audio=step["file_id"],
                reply_markup=inline_btn("Записаться", "signup")
            )
        elif step["type"] == "document":
            await bot.send_document(
                user_id,
                document=step["file_id"],
                reply_markup=inline_btn("Записаться", "signup")
            )
        elif step["type"] == "photo":
            await bot.send_photo(
                user_id,
                photo=step["file_id"],
                caption=step.get("caption", ""),
                reply_markup=inline_btn("Записаться", "signup")
            )
        log_to_sheet(user_id, None, step["description"], "auto_sent")
    except Exception as e:
        logging.error(f"Ошибка авто-шага: {e}")

@dp.callback_query(F.data == "signup")
async def handle_signup(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id

    for step in auto_funnel:
        try:
            scheduler.remove_job(f"auto_{user_id}_{step['description']}")
        except:
            pass

    log_to_sheet(user_id, None, "manual_signup", "signed_up")
    url = f"https://t.me/{OWNER_USERNAME}?start=хочу_записаться_на_ретрит"
    await callback.message.answer(
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
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    asyncio.run(run_bot())


