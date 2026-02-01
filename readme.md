# Discord Calendar Bot

Google Calendarから新規追加された予定を検出し、毎朝7:00に指定したDiscordチャンネルへ通知するBotです。

## 機能

- Google Calendarから今日〜1ヶ月先の予定を取得
- 前日と比較して新規追加された予定のみを抽出
- 毎朝7:00(日本時間)に自動通知
- 新規予定がない場合は通知をスキップ
- 複数のカレンダーを同時監視可能(個人カレンダー、ファミリーカレンダーなど)

## 必要要件

- Python 3.8以上
- Googleアカウント
- Discordアカウントとサーバー

---

## セットアップ手順

### 1. リポジトリのクローンとライブラリのインストール

```bash
# 仮想環境を作成(推奨)
python -m venv venv

# 仮想環境を有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 依存ライブラリをインストール
pip install -r requirements.txt
```

### 2. Google Calendar APIの設定

#### 2.1 Google Cloud Consoleでプロジェクトを作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成
3. プロジェクト名を入力(例: "Discord Calendar Bot")

#### 2.2 Calendar APIを有効化

1. 左側メニューから「APIとサービス」→「ライブラリ」を選択
2. 検索ボックスで「Google Calendar API」を検索
3. 「Google Calendar API」をクリック
4. 「有効にする」をクリック

#### 2.3 OAuth 2.0認証情報を作成

1. 左側メニューから「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「OAuth クライアントID」をクリック
3. 同意画面の構成を求められたら、以下を設定:
   - ユーザータイプ: **外部**
   - アプリ名: 任意(例: "Discord Calendar Bot")
   - ユーザーサポートメール: 自分のメールアドレス
   - デベロッパーの連絡先: 自分のメールアドレス
   - 「保存して次へ」をクリック
   - スコープは設定不要(スキップ)
   - テストユーザーに自分のGoogleアカウントを追加
4. 再度「認証情報を作成」→「OAuth クライアントID」をクリック
5. アプリケーションの種類: **デスクトップアプリ**
6. 名前: 任意(例: "Calendar Bot Client")
7. 「作成」をクリック
8. **credentials.jsonをダウンロード**

#### 2.4 credentials.jsonを配置

```bash
# credentialsフォルダを作成
mkdir credentials

# ダウンロードしたcredentials.jsonをcredentials/フォルダに移動
```

### 3. Discord Botの設定

#### 3.1 Botアプリケーションを作成

1. [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
2. 「New Application」をクリック
3. アプリケーション名を入力(例: "Calendar Bot")
4. 「Create」をクリック

#### 3.2 Botユーザーを追加

1. 左側メニューから「Bot」を選択
2. 「Add Bot」→「Yes, do it!」をクリック
3. **TOKEN**をコピー(後で.envファイルに使用)
   - 「Reset Token」をクリックしてトークンを表示
   - トークンは一度しか表示されないので必ず保存

#### 3.3 Bot権限の設定

1. 「Bot」ページで以下を有効化:
   - MESSAGE CONTENT INTENT: **ON**
2. 左側メニューから「OAuth2」→「URL Generator」を選択
3. **SCOPES**で以下を選択:
   - `bot`
4. **BOT PERMISSIONS**で以下を選択:
   - `Send Messages`
   - `View Channels`
5. 下部に生成されたURLをコピー

#### 3.4 Botをサーバーに招待

1. コピーしたURLをブラウザで開く
2. Botを追加したいサーバーを選択
3. 「認証」をクリック

#### 3.5 チャンネルIDを取得

1. Discordアプリで「ユーザー設定」→「詳細設定」→「開発者モード」を**ON**にする
2. 通知を送りたいチャンネルを右クリック
3. 「IDをコピー」をクリック

### 4. カレンダーIDを取得

#### 4.1 個人カレンダー(primary)

個人のメインカレンダーを使用する場合は、IDは`primary`です。

#### 4.2 ファミリーカレンダーや共有カレンダー

1. [Google Calendar](https://calendar.google.com/)をブラウザで開く
2. 左側のカレンダーリストから対象のカレンダー(例: 「ファミリー」)を探す
3. カレンダー名の右側にある **︙** (3点メニュー)をクリック
4. 「設定と共有」を選択
5. 下にスクロールして「カレンダーの統合」セクションを見つける
6. **カレンダーID**をコピー
   - 例: `family04585376700988033134@group.calendar.google.com`

### 5. 環境変数の設定

#### 5.1 .envファイルを作成

```bash
# .env.exampleをコピーして.envを作成
cp .env.example .env
```

#### 5.2 .envファイルを編集

`.env`ファイルを開いて、以下の値を設定:

```env
# Discord設定
DISCORD_BOT_TOKEN=取得したDiscord Botトークン
DISCORD_CHANNEL_ID=取得したチャンネルID(数値のみ)

# Google Calendar設定
GOOGLE_CREDENTIALS_PATH=credentials/credentials.json
GOOGLE_TOKEN_PATH=credentials/token.json

# カレンダーID (カンマ区切りで複数指定可能)
# 例1: 個人カレンダーのみ
CALENDAR_IDS=primary

# 例2: ファミリーカレンダーのみ
# CALENDAR_IDS=family04585376700988033134@group.calendar.google.com

# 例3: 個人カレンダーとファミリーカレンダーの両方
# CALENDAR_IDS=primary,family04585376700988033134@group.calendar.google.com

# スケジュール設定
NOTIFICATION_TIME=07:00
TIMEZONE=Asia/Tokyo
EVENT_FETCH_DAYS=30

# データストレージ
STORAGE_PATH=data/previous_events.json
```

### 6. テスト実行

Google Calendar APIの接続をテスト:

```bash
python test_calendar.py
```

**初回実行時:**
- ブラウザが自動で開きます
- Googleアカウントでログイン
- アクセス許可を承認
- `credentials/token.json`が自動生成されます

**成功例:**
```
============================================================
Google Calendar API 接続テスト
============================================================

設定を読み込み中...
  認証ファイル: credentials/credentials.json
  トークンファイル: credentials/token.json
  カレンダーID: primary
  監視カレンダー数: 1個
  タイムゾーン: Asia/Tokyo
  取得期間: 今日から30日間

Google Calendar APIに接続中...
✓ 接続成功

予定を取得中 (今日から30日間)...
[primary] 5件のイベントを取得しました

✓ 5件の予定が見つかりました:
...
```

### 7. Bot起動

```bash
python main.py
```

**起動メッセージ例:**
```
==================================================
Discord Calendar Bot
==================================================
✓ 環境変数の検証が完了しました
✓ 必要なディレクトリを作成しました
✓ 通知時刻: 07:00
✓ タイムゾーン: Asia/Tokyo
✓ 予定取得範囲: 今日から30日間
✓ 監視カレンダー: 1個
  1. primary

スケジューラーを起動しました (実行時刻: 07:00)
次回実行: 2026/02/02 07:00:00
待機時間: 18.5時間
```

Botは常時起動したままにしてください。毎朝7:00に自動実行されます。

---

## 使い方

### 基本動作

1. Botは毎朝7:00に自動起動します
2. Google Calendarから今日〜30日先の予定を取得
3. 前日と比較して新規追加された予定を検出
4. 新規予定があればDiscordに通知
5. 新規予定がなければ何もしない

### 通知メッセージの例

```
📅 **新しい予定が追加されました**

• **プロジェクトミーティング** - 2026/02/05 14:00
• **定例会議** - 2026/02/10 10:00
• **クライアント打ち合わせ** - 2026/02/15 15:30
```

### 手動で停止する方法

```
Ctrl + C
```

---

## トラブルシューティング

### Q1. 初回認証時にブラウザが開かない

- `credentials.json`が正しいパスに配置されているか確認
- Google Cloud ConsoleでOAuth同意画面が正しく設定されているか確認

### Q2. Discord通知が届かない

- `.env`ファイルの`DISCORD_BOT_TOKEN`が正しいか確認
- `DISCORD_CHANNEL_ID`が正しいか確認(数値のみ)
- BotがDiscordサーバーに招待されているか確認
- Botに`Send Messages`と`View Channels`の権限があるか確認

### Q3. カレンダーIDが見つからない(404エラー)

```
Calendar API エラー [family123@group.calendar.google.com]: <HttpError 404 "Not Found">
```

- カレンダーIDが正しいか確認
- Google Calendarの「設定と共有」→「カレンダーの統合」からIDをコピー
- `.env`ファイルの`CALENDAR_IDS`を正しいIDに変更

### Q4. 認証トークンエラー

`token.json`を削除して再認証:

```bash
rm credentials/token.json
python test_calendar.py
```

### Q5. タイムゾーンがずれる

- `.env`ファイルの`TIMEZONE`が`Asia/Tokyo`になっているか確認
- OSのタイムゾーン設定を確認

### Q6. 毎日7:00に実行されない

- サーバー/PCが常時起動しているか確認
- プロセスが異常終了していないか確認
- ログを確認してエラーがないかチェック

---

## ファイル構成

```
Calendarbot/
├── main.py                    # メインプログラム
├── config.py                  # 設定管理
├── google_calendar.py         # Google Calendar API連携
├── discord_notifier.py        # Discord通知機能
├── event_storage.py           # イベントデータ永続化
├── scheduler.py               # スケジューリング機能
├── test_calendar.py           # テストスクリプト
├── requirements.txt           # 依存ライブラリ
├── .env                       # 環境変数(作成が必要)
├── .env.example              # 環境変数テンプレート
├── .gitignore                # Git除外設定
├── readme.md                 # このファイル
├── data/                     # データ保存ディレクトリ(自動生成)
│   └── previous_events.json  # 前日のイベント保存
└── credentials/              # 認証情報ディレクトリ(作成が必要)
    ├── credentials.json      # Google API認証情報
    └── token.json            # OAuth トークン(自動生成)
```

---

## カスタマイズ

### 通知時刻を変更

`.env`ファイルの`NOTIFICATION_TIME`を変更:

```env
# 朝9時に通知
NOTIFICATION_TIME=09:00

# 夜8時に通知
NOTIFICATION_TIME=20:00
```

### 予定取得範囲を変更

`.env`ファイルの`EVENT_FETCH_DAYS`を変更:

```env
# 1週間先まで
EVENT_FETCH_DAYS=7

# 2ヶ月先まで
EVENT_FETCH_DAYS=60
```

### 複数カレンダーの監視

`.env`ファイルの`CALENDAR_IDS`にカンマ区切りで追加:

```env
CALENDAR_IDS=primary,family04585376700988033134@group.calendar.google.com,work@group.calendar.google.com
```

---

## ライセンス

MIT License

---

## 注意事項

- `.env`ファイルと`credentials/`フォルダは絶対にGitにコミットしないでください(`.gitignore`で除外済み)
- Discord BotトークンとGoogle認証情報は機密情報として適切に管理してください
- Botを常時起動するには、サーバーまたは24時間稼働するPCが必要です
