import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """環境変数を一元管理するクラス"""

    # Discord設定
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

    # Google Calendar設定
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/credentials.json')
    GOOGLE_TOKEN_PATH = os.getenv('GOOGLE_TOKEN_PATH', 'credentials/token.json')
    _CALENDAR_IDS_RAW = os.getenv('CALENDAR_IDS', 'primary')

    # カレンダーIDをリストに変換(カンマ区切り対応)
    CALENDAR_IDS = [cid.strip() for cid in _CALENDAR_IDS_RAW.split(',') if cid.strip()]

    # スケジュール設定
    NOTIFICATION_TIME = os.getenv('NOTIFICATION_TIME', '07:00')
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Tokyo')
    EVENT_FETCH_DAYS = int(os.getenv('EVENT_FETCH_DAYS', '30'))

    # ストレージ設定
    STORAGE_PATH = os.getenv('STORAGE_PATH', 'data/previous_events.json')

    @classmethod
    def validate(cls):
        """必須環境変数のバリデーション"""
        required = {
            'DISCORD_BOT_TOKEN': cls.DISCORD_BOT_TOKEN,
            'DISCORD_CHANNEL_ID': cls.DISCORD_CHANNEL_ID,
        }

        missing = [var for var, value in required.items() if not value]
        if missing:
            raise ValueError(f"必須環境変数が設定されていません: {', '.join(missing)}")

        # チャンネルIDを整数に変換して検証
        try:
            cls.DISCORD_CHANNEL_ID = int(cls.DISCORD_CHANNEL_ID)
        except (ValueError, TypeError):
            raise ValueError("DISCORD_CHANNEL_IDは数値である必要があります")
