import asyncio
import os
from config import Config
from google_calendar import GoogleCalendarClient
from discord_notifier import DiscordNotifier
from event_storage import EventStorage
from scheduler import DailyScheduler

async def daily_notification_task():
    """毎日実行されるメインタスク"""

    print("カレンダーチェックを開始します...")

    try:
        # 1. Google Calendarからイベント取得(複数カレンダー対応)
        calendar = GoogleCalendarClient(
            credentials_path=Config.GOOGLE_CREDENTIALS_PATH,
            token_path=Config.GOOGLE_TOKEN_PATH,
            timezone=Config.TIMEZONE
        )
        current_events = calendar.get_upcoming_events_from_multiple_calendars(
            days=Config.EVENT_FETCH_DAYS,
            calendar_ids=Config.CALENDAR_IDS
        )

        # 2. 新規イベントを検出
        storage = EventStorage(Config.STORAGE_PATH)
        new_events = storage.get_new_events(current_events)

        # 3. Discord通知(新規イベントがある場合のみ)
        if new_events:
            print(f"\n{len(new_events)}件の新規予定が見つかりました:")
            for event in new_events:
                print(f"  - {event['title']} ({event['start']})")

            notifier = DiscordNotifier(
                bot_token=Config.DISCORD_BOT_TOKEN,
                channel_id=Config.DISCORD_CHANNEL_ID
            )
            await notifier.send_notification(new_events)
        else:
            print("新規予定はありません")

        # 4. 現在のイベントを保存(次回比較用)
        storage.save_events(current_events)
        print("イベントデータを保存しました")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """メインエントリーポイント"""

    print("=" * 50)
    print("Discord Calendar Bot")
    print("=" * 50)

    try:
        # 設定検証
        Config.validate()
        print("✓ 環境変数の検証が完了しました")

        # 必要なディレクトリを作成
        os.makedirs('data', exist_ok=True)
        os.makedirs('credentials', exist_ok=True)
        print("✓ 必要なディレクトリを作成しました")

        # スケジューラー起動
        scheduler = DailyScheduler(
            target_time=Config.NOTIFICATION_TIME,
            timezone=Config.TIMEZONE
        )

        print(f"✓ 通知時刻: {Config.NOTIFICATION_TIME}")
        print(f"✓ タイムゾーン: {Config.TIMEZONE}")
        print(f"✓ 予定取得範囲: 今日から{Config.EVENT_FETCH_DAYS}日間")
        print(f"✓ 監視カレンダー: {len(Config.CALENDAR_IDS)}個")
        for i, cal_id in enumerate(Config.CALENDAR_IDS, 1):
            print(f"  {i}. {cal_id}")
        print()

        # 毎日定期実行
        await scheduler.run_daily(daily_notification_task)

    except ValueError as e:
        print(f"\n設定エラー: {e}")
        print("\n.envファイルを確認してください。")
        print("参考: .env.exampleを.envにコピーして必要な値を設定してください。")
    except KeyboardInterrupt:
        print("\n\nBotを終了します...")
    except Exception as e:
        print(f"\n予期しないエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
