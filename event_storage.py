import json
import os
from typing import List, Dict, Any

class EventStorage:
    """イベントデータの永続化と差分検出を行うクラス"""

    def __init__(self, storage_path: str = 'data/previous_events.json'):
        """
        Args:
            storage_path: JSONファイルの保存パス
        """
        self.storage_path = storage_path

    def save_events(self, events: List[Dict[str, Any]]) -> None:
        """
        イベントリストをJSONファイルに保存

        Args:
            events: イベントリスト [{'id': str, 'title': str, 'start': str, 'end': str}, ...]
        """
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        # イベントIDをキーとした辞書形式で保存
        events_dict = {event['id']: event for event in events}

        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(events_dict, f, ensure_ascii=False, indent=2)

    def load_events(self) -> Dict[str, Dict[str, Any]]:
        """
        前回保存したイベントを読み込み

        Returns:
            イベント辞書 {'event_id': {'id': str, 'title': str, 'start': str, 'end': str}, ...}
            ファイルが存在しない場合は空辞書を返す
        """
        if not os.path.exists(self.storage_path):
            return {}

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # JSONファイルが破損している場合は空辞書を返す
            print(f"警告: {self.storage_path}が破損しています。空データで初期化します。")
            return {}

    def get_new_events(self, current_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        前回のイベントと比較して新規追加されたイベントのみを抽出

        Args:
            current_events: 現在のイベントリスト

        Returns:
            新規イベントリスト
        """
        previous_events = self.load_events()
        previous_ids = set(previous_events.keys())
        current_ids = {event['id'] for event in current_events}

        # 新規追加されたイベントIDを特定
        new_ids = current_ids - previous_ids

        # 新規イベントのみを抽出
        new_events = [event for event in current_events if event['id'] in new_ids]

        return new_events
