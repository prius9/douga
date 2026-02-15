# Googleスプレッドシート テンプレート

このシステムで使用するGoogleスプレッドシートのテンプレートです。

## スプレッドシート構成

以下の3つのワークシートを作成してください：

### 1. Topics（トピック一覧）

トピックのマスターリストを管理します。

| Column A | Column B |
|----------|----------|
| Category | Topic |

**例:**

| Category | Topic |
|----------|-------|
| テクノロジー | AI技術の最新動向 |
| テクノロジー | プログラミング言語の選び方 |
| テクノロジー | Web開発のベストプラクティス |
| ビジネス | 効果的なプレゼンテーション技術 |
| ビジネス | リモートワークの生産性向上 |
| 教育・学習 | 効率的な学習方法 |
| 教育・学習 | 記憶力を高めるテクニック |
| ライフスタイル | 時間管理術 |
| ライフスタイル | ストレス解消法 |

### 2. Schedule（スケジュール管理）

毎日の動画生成スケジュールを管理します。

| Column A | Column B | Column C | Column D | Column E |
|----------|----------|----------|----------|----------|
| Date | Topic | Duration | Style | Notes |

**例:**

| Date | Topic | Duration | Style | Notes |
|------|-------|----------|-------|-------|
| 2026-02-15 | AI技術の最新動向 | 60 | informative | トレンド重視 |
| 2026-02-16 | プログラミング言語の選び方 | 90 | educational | 初心者向け |
| 2026-02-17 | 時間管理術 | 60 | entertaining | 実践的な内容 |
| 2026-02-18 | リモートワークの生産性向上 | 75 | informative | 在宅勤務者向け |

**フィールド説明:**
- **Date**: 日付（YYYY-MM-DD形式）
- **Topic**: 動画のトピック
- **Duration**: 動画の長さ（秒）
- **Style**: 動画のスタイル（informative/entertaining/educational）
- **Notes**: メモ（任意）

### 3. Templates（コンテンツテンプレート）

動画のテンプレートを管理します（オプション）。

| Column A | Column B | Column C | Column D |
|----------|----------|----------|----------|
| Template Name | Opening | Main Content Style | Closing |

**例:**

| Template Name | Opening | Main Content Style | Closing |
|---------------|---------|-------------------|---------|
| default | こんにちは！今日は{topic}についてお話しします | 箇条書き3点 | ご視聴ありがとうございました！ |
| casual | やあ！{topic}について解説するよ | 会話形式 | また見てね！ |
| formal | 本日のテーマは{topic}です | 詳細説明 | 以上です。ありがとうございました。 |

### 4. GenerationLog（生成ログ）

動画生成の履歴を自動記録します（システムが自動作成）。

| Column A | Column B | Column C | Column D | Column E | Column F | Column G | Column H |
|----------|----------|----------|----------|----------|----------|----------|----------|
| Timestamp | Topic | Duration | Style | Success | Script Path | Video Path | Notes |

このワークシートはシステムが自動的に更新します。

## セットアップ手順

### 1. スプレッドシートの作成

1. [Google Sheets](https://sheets.google.com/)にアクセス
2. 新しいスプレッドシートを作成
3. 上記の構成に従って3つのワークシートを作成
   - Topics
   - Schedule
   - Templates（オプション）

### 2. サービスアカウントの作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを選択）
3. 「APIとサービス」→「認証情報」に移動
4. 「認証情報を作成」→「サービスアカウント」を選択
5. サービスアカウント名を入力（例: video-generation-bot）
6. 「完了」をクリック

### 3. 認証キーのダウンロード

1. 作成したサービスアカウントをクリック
2. 「キー」タブに移動
3. 「鍵を追加」→「新しい鍵を作成」
4. JSON形式を選択してダウンロード
5. ダウンロードしたファイルを `config/google_credentials.json` として保存

### 4. APIの有効化

1. Google Cloud Consoleで「APIとサービス」→「ライブラリ」に移動
2. 以下のAPIを検索して有効化：
   - Google Sheets API
   - Google Drive API

### 5. スプレッドシートの共有

1. 作成したスプレッドシートを開く
2. 「共有」ボタンをクリック
3. サービスアカウントのメールアドレスを入力
   - 形式: `[service-account-name]@[project-id].iam.gserviceaccount.com`
4. 権限を「編集者」に設定（ログ記録のため）
5. 「送信」をクリック

### 6. スプレッドシートIDの取得

スプレッドシートのURLから、IDをコピーします：

```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
                                        ^^^^^^^^^^^^^^
                                        この部分がID
```

### 7. 環境変数の設定

`.env`ファイルに以下を追加：

```bash
USE_GOOGLE_SHEETS=true
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id_here
GOOGLE_CREDENTIALS_PATH=./config/google_credentials.json
```

## 使用方法

### スプレッドシートから今日のトピックを取得

```bash
python main.py --topic-strategy sheet
```

システムは以下の順序で動作します：
1. Scheduleシートから今日の日付のトピックを検索
2. 見つかった場合はそのトピックを使用
3. 見つからない場合はランダム選択にフォールバック

### スプレッドシートからトピックリストを取得

TopicsシートのデータがYAMLファイルの代わりに使用されます。

```bash
# USE_GOOGLE_SHEETS=trueの場合、自動的にスプレッドシートから読み込まれます
python main.py --topic-strategy random
```

## トラブルシューティング

### 認証エラー

```
google.auth.exceptions.DefaultCredentialsError
```

→ `google_credentials.json`ファイルが正しい場所にあるか確認してください。

### 権限エラー

```
gspread.exceptions.APIError: 403
```

→ スプレッドシートがサービスアカウントと共有されているか確認してください。

### データが取得できない

1. スプレッドシートIDが正しいか確認
2. ワークシート名が正しいか確認（"Topics", "Schedule"など）
3. データの形式が正しいか確認

## スプレッドシートテンプレートのコピー

以下のリンクからテンプレートをコピーできます（将来的に作成予定）：

[テンプレートをコピー](#)

## サンプルデータ

### Topicsシート サンプル

```csv
Category,Topic
テクノロジー,AI技術の最新動向
テクノロジー,プログラミング言語の選び方
テクノロジー,Web開発のベストプラクティス
ビジネス,効果的なプレゼンテーション技術
ビジネス,リモートワークの生産性向上
教育・学習,効率的な学習方法
教育・学習,記憶力を高めるテクニック
ライフスタイル,時間管理術
ライフスタイル,ストレス解消法
```

### Scheduleシート サンプル

```csv
Date,Topic,Duration,Style,Notes
2026-02-15,AI技術の最新動向,60,informative,トレンド重視
2026-02-16,プログラミング言語の選び方,90,educational,初心者向け
2026-02-17,時間管理術,60,entertaining,実践的な内容
2026-02-18,リモートワークの生産性向上,75,informative,在宅勤務者向け
```
