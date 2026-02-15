# Claude to Vrew 自動動画生成システム

ClaudeとVrewを組み合わせて、毎日自動的に動画を生成するシステムです。Claude APIでスクリプトを自動生成し、Vrewで動画化します。

## 特徴

- **自動スクリプト生成**: Claude APIを使用して、魅力的な動画スクリプトを自動生成
- **トピック自動選定**: トレンド分析やカテゴリ別選択で毎日異なるトピックを提供
- **Googleスプレッドシート連携**: スプレッドシートから毎日のトピックやスケジュールを管理
- **Vrew連携**: Vrewが読み込める形式（SRT、JSON、テキスト）でファイルを出力
- **スケジューリング**: GitHub ActionsまたはCronで毎日定時実行
- **カスタマイズ可能**: トピック、スタイル、動画の長さなどを柔軟に設定

## システム構成

```
douga/
├── .github/
│   └── workflows/
│       └── daily-video-generation.yml  # GitHub Actionsワークフロー
├── src/
│   ├── claude_script_generator.py      # Claude APIでスクリプト生成
│   ├── vrew_integration.py             # Vrew連携モジュール
│   ├── topic_selector.py               # トピック自動選定
│   ├── google_sheets_integration.py    # Google Sheets連携
│   └── video_pipeline.py               # パイプライン管理
├── config/
│   ├── topics.yaml                     # トピック設定
│   └── config.yaml.example             # システム設定例
├── templates/
│   └── vrew_project_template.json      # Vrewプロジェクトテンプレート
├── output/                             # 出力ディレクトリ
│   ├── scripts/                        # 生成されたスクリプト
│   ├── vrew_projects/                  # Vrew用プロジェクトファイル
│   └── videos/                         # レンダリングされた動画
├── logs/                               # ログファイル
├── main.py                             # メインスクリプト
├── requirements.txt                    # Python依存関係
└── README.md                           # このファイル
```

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd douga
```

### 2. Python環境のセットアップ

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env`ファイルを作成して、必要な環境変数を設定します：

```bash
cp .env.example .env
```

`.env`ファイルを編集：

```bash
# Claude API Key（必須）
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Vrew CLI（オプション）
VREW_CLI_PATH=/path/to/vrew/cli

# 出力フォルダ
VREW_WATCH_FOLDER=./output/vrew_projects
VREW_OUTPUT_FOLDER=./output/videos
```

### 4. Claude API Keyの取得

1. [Anthropic Console](https://console.anthropic.com/)にアクセス
2. API Keyを生成
3. `.env`ファイルに設定

## 使い方

### 手動実行

#### 基本的な使い方

```bash
python main.py
```

#### トピックを指定して実行

```bash
python main.py --topic "AI技術の最新動向"
```

#### トピック選択戦略を指定

```bash
# ランダム選択
python main.py --topic-strategy random

# トレンディングトピック
python main.py --topic-strategy trending

# カテゴリ指定
python main.py --topic-strategy category --category "テクノロジー"

# Googleスプレッドシートから取得
python main.py --topic-strategy sheet
```

#### 複数の動画を生成

```bash
python main.py --count 3 --topic-strategy random
```

#### 動画の長さとスタイルを指定

```bash
python main.py --duration 90 --style entertaining
```

### 自動実行の設定

#### GitHub Actionsを使用（推奨）

1. GitHub Secretsに`ANTHROPIC_API_KEY`を設定
2. `.github/workflows/daily-video-generation.yml`が自動的に実行されます
3. 毎日午前7時（JST）に自動実行
4. 手動実行も可能（Actionsタブから）

#### Cronを使用

```bash
# Cron設定スクリプトを実行
bash cron-setup.sh

# crontabを編集
crontab -e

# 以下を追加（毎日午前7時に実行）
0 7 * * * /path/to/douga/run-daily-video.sh
```

## ワークフロー

### 自動生成フロー

```
毎日午前7時
  ↓
1. トピック選定
   - ランダム選択
   - トレンド分析
   - カテゴリ指定
  ↓
2. Claude APIでスクリプト生成
   - ナレーション原稿
   - 字幕テキスト
   - 視覚的な指示
  ↓
3. Vrew用ファイル生成
   - SRTファイル（字幕）
   - JSONプロジェクト
   - テキストスクリプト
  ↓
4. Vrewでレンダリング（オプション）
   - CLI経由で自動レンダリング
   - または手動でVrewにインポート
  ↓
5. 完成した動画を保存
  ↓
6. 通知（オプション）
   - Slack通知
   - メール通知
```

## Vrewとの連携

### 手動インポート

1. `output/vrew_projects/` フォルダに生成されたファイルを確認
2. Vrewを起動
3. 以下のいずれかの方法でインポート：
   - **SRTファイル**: 字幕として読み込み
   - **テキストファイル**: スクリプトとして読み込み
   - **JSONファイル**: プロジェクトとして読み込み（.vrewファイル）

### 自動レンダリング（Vrew CLIがある場合）

Vrew CLIがインストールされている場合、自動レンダリングが可能です：

```bash
python main.py --auto-render
```

## トピックのカスタマイズ

`config/topics.yaml`ファイルを編集して、独自のトピックを追加できます：

```yaml
- category: カスタムカテゴリ
  topics:
    - トピック1
    - トピック2
    - トピック3
```

## Googleスプレッドシート連携

Googleスプレッドシートから動画のトピックやスケジュールを管理できます。

### セットアップ

1. **スプレッドシートの準備**
   - 新しいGoogleスプレッドシートを作成
   - 「Topics」「Schedule」シートを作成
   - 詳細は [`docs/google-sheets-template.md`](docs/google-sheets-template.md) を参照

2. **サービスアカウントの作成**
   - Google Cloud Consoleでサービスアカウントを作成
   - 認証キー（JSON）をダウンロード
   - `config/google_credentials.json` として保存

3. **環境変数の設定**

```bash
USE_GOOGLE_SHEETS=true
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id_here
GOOGLE_CREDENTIALS_PATH=./config/google_credentials.json
```

4. **スプレッドシートの共有**
   - サービスアカウントのメールアドレスと共有
   - 編集権限を付与

### 使い方

#### 今日のトピックをスプレッドシートから取得

```bash
python main.py --topic-strategy sheet
```

システムは以下の順序で動作：
1. Scheduleシートから今日の日付のトピックを検索
2. 見つかった場合はそのトピックを使用
3. 見つからない場合はランダム選択にフォールバック

#### スプレッドシート形式

**Topicsシート:**
```
| Category    | Topic              |
|-------------|-------------------|
| テクノロジー | AI技術の最新動向    |
| ビジネス     | リモートワークのコツ |
```

**Scheduleシート:**
```
| Date       | Topic           | Duration | Style       |
|------------|-----------------|----------|-------------|
| 2026-02-15 | AI技術の最新動向 | 60       | informative |
```

詳細なテンプレートと設定方法は [`docs/google-sheets-template.md`](docs/google-sheets-template.md) を参照してください。

## コマンドラインオプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--topic` | 動画のトピック | 自動選択 |
| `--topic-strategy` | トピック選択戦略（random/trending/category/sheet） | random |
| `--category` | カテゴリ指定 | - |
| `--duration` | 動画の長さ（秒） | 60 |
| `--style` | 動画のスタイル（informative/entertaining/educational） | informative |
| `--count` | 生成する動画の数 | 1 |
| `--auto-render` | 自動レンダリング | False |
| `--log-level` | ログレベル（DEBUG/INFO/WARNING/ERROR） | INFO |
| `--output-dir` | 出力ディレクトリ | ./output |

## 出力ファイル

### スクリプトファイル（JSON）

```json
{
  "title": "動画のタイトル",
  "description": "動画の説明",
  "total_duration": 60,
  "scenes": [
    {
      "scene_number": 1,
      "start_time": 0,
      "end_time": 10,
      "narration": "ナレーション原稿",
      "subtitle": "字幕テキスト",
      "visual_instructions": "画面表示の指示"
    }
  ],
  "keywords": ["キーワード"],
  "hashtags": ["#ハッシュタグ"]
}
```

### SRTファイル（字幕）

```
1
00:00:00,000 --> 00:00:10,000
オープニングの字幕

2
00:00:10,000 --> 00:00:20,000
メインコンテンツの字幕
```

## トラブルシューティング

### API Keyエラー

```
ValueError: ANTHROPIC_API_KEY が設定されていません
```

→ `.env`ファイルに正しいAPI Keyが設定されているか確認してください。

### Vrew CLIが見つからない

```
Vrew CLIが見つかりません
```

→ Vrew CLIのパスを`.env`ファイルに設定するか、手動でVrewにファイルをインポートしてください。

### パッケージのインストールエラー

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 開発とカスタマイズ

### モジュール構成

- **claude_script_generator.py**: Claude APIを使用したスクリプト生成ロジック
- **vrew_integration.py**: Vrewとの連携、ファイルフォーマット変換
- **topic_selector.py**: トピック選定アルゴリズム
- **video_pipeline.py**: 全体のパイプライン管理

### 拡張例

#### カスタムトピック選定アルゴリズム

```python
from src.topic_selector import TopicSelector

class CustomTopicSelector(TopicSelector):
    def select_custom_topic(self):
        # 独自のロジックを実装
        pass
```

#### 通知機能の追加

```python
# Slack通知の例
import requests

def send_slack_notification(message):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    requests.post(webhook_url, json={"text": message})
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

Issue報告やPull Requestは大歓迎です！

## サポート

質問や問題がある場合は、Issuesで報告してください。

## 更新履歴

### v1.0.0 (2026-02-15)

- 初回リリース
- Claude APIでスクリプト自動生成
- Vrew連携機能
- GitHub Actions/Cron対応
- トピック自動選定機能
