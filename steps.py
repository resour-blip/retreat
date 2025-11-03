# steps.py

# Это file_id именно от ВИДЕОКРУЖКА (поле "video_note" в @RawDataBot)
WELCOME_MEDIA_FILE_ID = "DQACAgIAAxkBAAE9TKNpB2e_tCGXA6_h0Z28zjgV_V6YVwACJYIAAlIlsEoAAaGqCo0rmKY2BA"

# Обязательно установи "video_note", чтобы отправлялся кружок
WELCOME_MEDIA_TYPE = "video_note"  # ← ключевое изменение!

REMINDER_TEXT = "Хочешь эксперимент? Он в видео 🎥"

# Основное видео (обычное, не кружок!)
MAIN_VIDEO_FILE_ID = "AAMCAgADGQEAAT1bJmkI6kVrBNE7JuEnNDQnr2B15hZ2AAJNiQACAulJSAAB54J_QndTJwEAB20AAzYE"
# Все шаги авто-воронки — ТОЛЬКО через file_id из Telegram (не Google Drive!)
auto_funnel = [
    {
        "type": "audio",
        "file_id": "YOUR_AUDIO_FILE_ID_1",  # ← замени на file_id из Telegram
        "delay_minutes_after_video": 30,
        "description": "objection_audio"
    },
    {
        "type": "audio",
        "file_id": "YOUR_AUDIO_FILE_ID_2",
        "delay_minutes_after_video": 60,
        "description": "case_krestina"
    },
    {
        "type": "document",
        "file_id": "YOUR_PDF_FILE_ID",
        "delay_minutes_after_video": 90,
        "description": "techniques_pdf"
    },
    {
        "type": "text",
        "content": "✨ Это твой шанс выйти из рутины и восстановиться по-настоящему...",
        "delay_minutes_after_video": 120,
        "description": "final_push"
    },
    {
        "type": "photo",
        "file_id": "YOUR_PHOTO_FILE_ID",
        "caption": "Ретрит проходит в уютном месте у моря. 3 дня полного присутствия.",
        "delay_minutes_after_video": 150,
        "description": "retreat_description"
    },
    {
        "type": "audio",
        "file_id": "YOUR_AUDIO_FILE_ID_3",
        "delay_minutes_after_video": 180,
        "description": "final_case"
    }
]

