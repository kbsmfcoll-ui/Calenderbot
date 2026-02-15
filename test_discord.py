"""
Discord Bot接続テストスクリプト

このスクリプトを実行して、Discord Botがチャンネルにメッセージを送信できるか確認できます。
"""

import asyncio
from config import Config
from discord_notifier import DiscordNotifier

async def main():
    print("=" * 60)
    print("Discord Bot 接続テスト")
    print("=" * 60)
    print()

    try:
        # 設定を読み込み
        print("設定を読み込み中...")
        print(f"  Botトークン: {Config.DISCORD_BOT_TOKEN[:20]}..." if Config.DISCORD_BOT_TOKEN else "  Botトークン: 未設定")
        print(f"  チャンネルID: {Config.DISCORD_CHANNEL_ID}")
        print()

        # 環境変数の検証
        Config.validate()
        print("✓ 環境変数の検証が完了しました")
        print()

        # テストイベントを作成
        print("テストメッセージを送信中...")
        test_events = [
            {
                'title': 'テストイベント1',
                'start': '2026-02-05T14:00:00+09:00',
                'end': '2026-02-05T15:00:00+09:00',
                'calendar_id': 'test'
            },
            {
                'title': 'テストイベント2',
                'start': '2026-02-10T10:00:00+09:00',
                'end': '2026-02-10T11:00:00+09:00',
                'calendar_id': 'test'
            }
        ]

        # Discord通知を送信
        notifier = DiscordNotifier(
            bot_token=Config.DISCORD_BOT_TOKEN,
            channel_id=Config.DISCORD_CHANNEL_ID
        )
        await notifier.send_notification(test_events)

        print()
        print("=" * 60)
        print("✓ テスト完了!")
        print("=" * 60)
        print()
        print("Discordチャンネルを確認してください。")
        print("テストメッセージが表示されていれば接続成功です。")

    except ValueError as e:
        print(f"\n❌ 設定エラー: {e}")
        print("\nセットアップ手順:")
        print("1. .env.exampleを.envにコピー")
        print("2. DISCORD_BOT_TOKENを設定")
        print("3. DISCORD_CHANNEL_IDを設定")
        print("\n参考: readme.mdのセットアップ手順を確認してください")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        print("\n考えられる原因:")
        print("- Botトークンが無効")
        print("- チャンネルIDが間違っている")
        print("- BotがDiscordサーバーに招待されていない")
        print("- Botに必要な権限(Send Messages, View Channels)がない")

if __name__ == '__main__':
    asyncio.run(main())
