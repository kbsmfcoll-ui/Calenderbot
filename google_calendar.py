import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

# 必要なスコープ(読み取り専用)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendarClient:
    """Google Calendar APIとの連携を行うクラス"""

    def __init__(self, credentials_path: str, token_path: str, timezone: str = 'Asia/Tokyo'):
        """
        Args:
            credentials_path: credentials.jsonのパス
            token_path: token.jsonのパス(自動生成される)
            timezone: タイムゾーン
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.timezone = pytz.timezone(timezone)
        self.service = None

    def _authenticate(self) -> Credentials:
        """
        OAuth 2.0認証を行う

        Returns:
            認証情報
        """
        creds = None

        # token.jsonが存在する場合は読み込む
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # 認証情報が無効または存在しない場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    # トークンをリフレッシュ
                    print("認証トークンを更新中...")
                    creds.refresh(Request())
                except Exception as e:
                    print(f"トークンの更新に失敗しました: {e}")
                    print("再認証が必要です。既存のトークンを削除して再認証を行います...")
                    # トークンファイルを削除
                    if os.path.exists(self.token_path):
                        os.remove(self.token_path)
                    creds = None

            if not creds or not creds.valid:
                # 初回認証フロー
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"認証ファイルが見つかりません: {self.credentials_path}\n"
                        "Google Cloud Consoleから credentials.json をダウンロードしてください。"
                    )

                print("初回認証を開始します。ブラウザで認証してください...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # 認証情報を保存
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            print(f"認証情報を保存しました: {self.token_path}")

        return creds

    def _get_service(self):
        """Calendar APIサービスを取得"""
        if not self.service:
            creds = self._authenticate()
            self.service = build('calendar', 'v3', credentials=creds)
        return self.service

    def get_upcoming_events(self, days: int = 30, calendar_id: str = 'primary') -> List[Dict[str, Any]]:
        """
        今日から指定日数先までの予定を取得

        Args:
            days: 取得する日数
            calendar_id: カレンダーID(デフォルトは'primary')

        Returns:
            イベントリスト [{'id': str, 'title': str, 'start': str, 'end': str, 'calendar_id': str}, ...]
        """
        try:
            service = self._get_service()

            # 今日の開始時刻(00:00:00)
            now = datetime.now(self.timezone).replace(hour=0, minute=0, second=0, microsecond=0)
            time_min = now.isoformat()

            # 指定日数後の終了時刻(23:59:59)
            time_max = (now + timedelta(days=days)).replace(hour=23, minute=59, second=59).isoformat()

            # イベント取得
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # イベント情報を整形
            formatted_events = []
            for event in events:
                # 開始時刻の取得(終日イベントと時刻指定イベントに対応)
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('summary', '(タイトルなし)'),
                    'start': start,
                    'end': end,
                    'calendar_id': calendar_id  # どのカレンダーからのイベントか記録
                })

            print(f"[{calendar_id}] {len(formatted_events)}件のイベントを取得しました")
            return formatted_events

        except HttpError as error:
            print(f"Calendar API エラー [{calendar_id}]: {error}")
            raise
        except Exception as error:
            print(f"予期しないエラー [{calendar_id}]: {error}")
            raise

    def get_upcoming_events_from_multiple_calendars(self, days: int = 30, calendar_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        複数のカレンダーから今日から指定日数先までの予定を取得

        Args:
            days: 取得する日数
            calendar_ids: カレンダーIDのリスト(デフォルトは['primary'])

        Returns:
            全カレンダーのイベントリスト [{'id': str, 'title': str, 'start': str, 'end': str, 'calendar_id': str}, ...]
        """
        if calendar_ids is None:
            calendar_ids = ['primary']

        all_events = []

        for calendar_id in calendar_ids:
            try:
                events = self.get_upcoming_events(days=days, calendar_id=calendar_id)
                all_events.extend(events)
            except Exception as e:
                print(f"警告: カレンダー '{calendar_id}' の取得に失敗しました: {e}")
                # エラーが発生しても他のカレンダーの取得は続行

        # 開始時刻でソート
        all_events.sort(key=lambda x: x['start'])

        print(f"\n合計 {len(all_events)}件のイベントを取得しました (全{len(calendar_ids)}カレンダー)")
        return all_events
