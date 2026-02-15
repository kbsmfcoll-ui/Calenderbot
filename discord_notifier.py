from datetime import datetime
from typing import List, Dict, Any
import discord

class DiscordNotifier:
    """Discord通知機能を提供するクラス"""

    def __init__(self, bot_token: str, channel_id: int):
        """
        Args:
            bot_token: Discord Botトークン
            channel_id: 通知先チャンネルID
        """
        self.bot_token = bot_token
        self.channel_id = channel_id

    def _format_datetime(self, dt_str: str) -> str:
        """
        日時文字列をフォーマット

        Args:
            dt_str: ISO形式の日時文字列

        Returns:
            フォーマットされた日時文字列 (例: 2026/02/05 14:00)
        """
        try:
            # dateTimeフィールドの場合(時刻指定あり)
            if 'T' in dt_str:
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                return dt.strftime('%Y/%m/%d %H:%M')
            # dateフィールドの場合(終日イベント)
            else:
                dt = datetime.strptime(dt_str, '%Y-%m-%d')
                return dt.strftime('%Y/%m/%d (終日)')
        except Exception as e:
            print(f"日時のフォーマットエラー: {e}")
            return dt_str

    def _format_events(self, events: List[Dict[str, Any]]) -> str:
        """
        イベントリストをメッセージ形式にフォーマット

        Args:
            events: イベントリスト

        Returns:
            フォーマットされたメッセージ
        """
        if not events:
            return ""

        # ヘッダー
        message_parts = ["📅 **新しい予定が追加されました**\n"]

        # 各イベントをフォーマット
        for event in events:
            title = event.get('title', '(タイトルなし)')
            start = self._format_datetime(event.get('start', ''))
            message_parts.append(f"• **{title}** - {start}")

        return "\n".join(message_parts)

    async def send_notification(self, events: List[Dict[str, Any]]) -> None:
        """
        新規イベントをDiscordに通知

        Args:
            events: 新規イベントリスト
        """
        # 新規イベントがない場合は送信しない
        if not events:
            print("新規イベントがないため、通知をスキップします")
            return

        # メッセージをフォーマット
        message = self._format_events(events)

        # Discordクライアントを作成して送信
        intents = discord.Intents.default()
        # このBotは送信のみで、メッセージ読み取りは不要
        intents.message_content = False
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            try:
                channel = await client.fetch_channel(self.channel_id)
                await channel.send(message)
                print(f"{len(events)}件の新規予定を通知しました")
            except discord.errors.NotFound:
                print(f"エラー: チャンネルID {self.channel_id} が見つかりません")
            except discord.errors.Forbidden:
                print("エラー: メッセージ送信の権限がありません")
            except Exception as e:
                print(f"Discord送信エラー: {e}")
            finally:
                # クライアントを適切にクローズ
                if not client.is_closed():
                    await client.close()

        try:
            await client.start(self.bot_token)
        except discord.errors.LoginFailure:
            print("エラー: Discord Botトークンが無効です")
        except Exception as e:
            print(f"Discord接続エラー: {e}")
        finally:
            # 万が一クローズされていない場合の保険
            if not client.is_closed():
                await client.close()
