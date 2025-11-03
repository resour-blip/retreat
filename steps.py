# steps.py

WELCOME_MEDIA_FILE_ID = "DQACAgIAAxkBAAE9TKNpB2e_tCGXA6_h0Z28zjgV_V6YVwACJYIAAlIlsEoAAaGqCo0rmKY2BA"  # ← замени на свой file_id
WELCOME_MEDIA_TYPE = "video"  # варианты: "video", "photo", "audio"

REMINDER_TEXT = "Хочешь эксперимент? Он в видео 🎥"

# 🔑 Вставь сюда file_id своего видео (полученный через @RawDataBot)
MAIN_VIDEO_FILE_ID = "AAMCAgADGQEAAT1M12kHb6x6u8iAx1Jz-b7rdeeU0N8iAAJwgwAC5TMoSCNm9p1D2FeBAQAHbQADNgQ"  # ← ОБЯЗАТЕЛЬНО замени!

auto_funnel = [
    {
        "type": "audio",
        "content": "https://drive.google.com/uc?export=download&id=ВАШ_AUDIO_ID_1",
        "delay_minutes_after_video": 30,
        "description": "objection_audio"
    },
    {
        "type": "audio",
        "content": "https://drive.google.com/uc?export=download&id=ВАШ_AUDIO_ID_2",
        "delay_minutes_after_video": 60,
        "description": "case_krestina"
    },
    {
        "type": "document",
        "content": "https://drive.google.com/uc?export=download&id=ВАШ_PDF_ID",
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
        "content": "https://drive.google.com/uc?export=download&id=ВАШ_PHOTO_ID",
        "caption": "Ретрит проходит в уютном месте у моря. 3 дня полного присутствия.",
        "delay_minutes_after_video": 150,
        "description": "retreat_description"
    },
    {
        "type": "audio",
        "content": "https://drive.google.com/uc?export=download&id=ВАШ_AUDIO_ID_3",
        "delay_minutes_after_video": 180,
        "description": "final_case"
    }

]


