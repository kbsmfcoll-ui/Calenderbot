import asyncio
from datetime import datetime, time, timedelta
from typing import Callable, Awaitable
import pytz

class DailyScheduler:
    """毎日指定時刻に処理を実行するスケジューラー"""

    def __init__(self, target_time: str = '07:00', timezone: str = 'Asia/Tokyo'):
        """
        Args:
            target_time: 実行時刻 (HH:MM形式)
            timezone: タイムゾーン
        """
        hour, minute = map(int, target_time.split(':'))
        self.target_time = time(hour=hour, minute=minute)
        self.timezone = pytz.timezone(timezone)

    def _get_next_run_time(self) -> datetime:
        """
        次回実行時刻を計算

        Returns:
            次回実行時刻
        """
        now = datetime.now(self.timezone)

        # 今日の実行時刻を生成
        target_datetime = self.timezone.localize(
            datetime.combine(now.date(), self.target_time)
        )

        # 今日の実行時刻を過ぎている場合は明日に設定
        if now >= target_datetime:
            target_datetime += timedelta(days=1)

        return target_datetime

    async def run_daily(self, callback: Callable[[], Awaitable[None]]) -> None:
        """
        毎日指定時刻にコールバック関数を実行

        Args:
            callback: 実行する非同期関数
        """
        print(f"スケジューラーを起動しました (実行時刻: {self.target_time.strftime('%H:%M')})")

        while True:
            # 次回実行時刻を計算
            next_run = self._get_next_run_time()
            now = datetime.now(self.timezone)
            wait_seconds = (next_run - now).total_seconds()

            print(f"次回実行: {next_run.strftime('%Y/%m/%d %H:%M:%S')}")
            print(f"待機時間: {wait_seconds / 3600:.1f}時間")

            # 次回実行時刻まで待機
            await asyncio.sleep(wait_seconds)

            # コールバック関数を実行
            print(f"\n--- {datetime.now(self.timezone).strftime('%Y/%m/%d %H:%M:%S')} ---")
            try:
                await callback()
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                import traceback
                traceback.print_exc()

            print("処理が完了しました\n")
