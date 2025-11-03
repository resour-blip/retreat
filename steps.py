# steps.py

# steps.py

# Убедись, что WELCOME_MEDIA_FILE_ID — это file_id обычного видео (поле "video" в @RawDataBot)
WELCOME_MEDIA_FILE_ID = "BAACAgIAAxkBAAE9VZFpCIIwnG4TMKU3y-rCp9o_6YkIGgAC24cAAsMWQUgl22cXW9ssPjYE"

# Варианты: "video", "photo", "audio" (НЕ "video_note"!)
WELCOME_MEDIA_TYPE = "video"

REMINDER_TEXT = "Хочешь эксперимент? Он в видео 🎥"

# 🔑 Вставь сюда file_id своего основного видео (полученный через @RawDataBot)
MAIN_VIDEO_FILE_ID = "BAACAgIAAxkBAAE9TNdpB2-servIgMdSc_m-63XnlNDfIgACcIMAAuUzKEgjZvadQ9hXgTYE"

auto_funnel = [
    {
        "type": "audio",
        "file_id": "YOUR_AUDIO_FILE_ID_1",  # ← замени на file_id из Telegram (не URL!)
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


