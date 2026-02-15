"""
Google Calendar API接続テストスクリプト

このスクリプトを実行して、Google Calendarから予定を取得できるか確認できます。
"""

import sys
import io

# Windows環境でのUnicode出力をサポート
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from config import Config
from google_calendar import GoogleCalendarClient

def main():
    print("=" * 60)
    print("Google Calendar API 接続テスト")
    print("=" * 60)
    print()

    try:
        # 設定を読み込み
        print("設定を読み込み中...")
        print(f"  認証ファイル: {Config.GOOGLE_CREDENTIALS_PATH}")
        print(f"  トークンファイル: {Config.GOOGLE_TOKEN_PATH}")
        print(f"  カレンダーID: {', '.join(Config.CALENDAR_IDS)}")
        print(f"  監視カレンダー数: {len(Config.CALENDAR_IDS)}個")
        print(f"  タイムゾーン: {Config.TIMEZONE}")
        print(f"  取得期間: 今日から{Config.EVENT_FETCH_DAYS}日間")
        print()

        # Google Calendar クライアントを初期化
        print("Google Calendar APIに接続中...")
        calendar = GoogleCalendarClient(
            credentials_path=Config.GOOGLE_CREDENTIALS_PATH,
            token_path=Config.GOOGLE_TOKEN_PATH,
            timezone=Config.TIMEZONE
        )
        print("✓ 接続成功")
        print()

        # 複数カレンダーからイベントを取得
        print(f"予定を取得中 (今日から{Config.EVENT_FETCH_DAYS}日間)...")
        print(f"監視対象: {len(Config.CALENDAR_IDS)}個のカレンダー")
        print()

        events = calendar.get_upcoming_events_from_multiple_calendars(
            days=Config.EVENT_FETCH_DAYS,
            calendar_ids=Config.CALENDAR_IDS
        )
        print()

        # 結果を表示
        if events:
            print(f"✓ {len(events)}件の予定が見つかりました:")
            print()
            print("-" * 60)
            for i, event in enumerate(events, 1):
                print(f"{i}. {event['title']}")
                print(f"   開始: {event['start']}")
                print(f"   終了: {event['end']}")
                print()
            print("-" * 60)
        else:
            print("⚠ 予定が見つかりませんでした")
            print("  (期間内に予定がないか、カレンダーが空の可能性があります)")

        print()
        print("=" * 60)
        print("テスト完了!")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"\n❌ エラー: {e}")
        print("\nセットアップ手順:")
        print("1. Google Cloud Consoleでプロジェクトを作成")
        print("2. Calendar APIを有効化")
        print("3. OAuth 2.0クライアントID(デスクトップアプリ)を作成")
        print("4. credentials.jsonをダウンロード")
        print(f"5. {Config.GOOGLE_CREDENTIALS_PATH} に配置")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
