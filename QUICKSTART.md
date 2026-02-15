# クイックスタートガイド

5分で始めるClaude to Vrew自動動画生成システム

## 最速セットアップ（3ステップ）

### ステップ1: 環境のセットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd douga

# Pythonパッケージをインストール
pip install -r requirements.txt
```

### ステップ2: API Keyの設定

`.env`ファイルを作成：

```bash
echo "ANTHROPIC_API_KEY=sk-ant-api03-YOUR_API_KEY_HERE" > .env
```

### ステップ3: 実行！

```bash
python main.py
```

これで完了です！`output/vrew_projects/`フォルダに生成されたファイルを確認してください。

## 生成されたファイルの使い方

### Vrewで動画を作成

1. Vrewアプリを起動
2. 以下のいずれかの方法でファイルをインポート：

#### 方法1: SRTファイルを使う（最も簡単）

```
output/vrew_projects/[プロジェクト名]/[プロジェクト名].srt
```

- Vrewで「新規作成」→「字幕ファイルから」
- SRTファイルを選択
- 自動的に字幕付き動画プロジェクトが作成されます

#### 方法2: テキストファイルを使う

```
output/vrew_projects/[プロジェクト名]/[プロジェクト名].txt
```

- Vrewで「新規作成」→「テキストから」
- テキストファイルを選択
- 内容を確認して動画を生成

#### 方法3: JSONプロジェクトファイルを使う（高度）

```
output/vrew_projects/[プロジェクト名].vrew
```

- Vrewで「ファイルを開く」
- .vrewファイルを選択
- プロジェクト全体が読み込まれます

## よくある使い方

### 特定のトピックで動画を作成

```bash
python main.py --topic "AIの基礎知識"
```

### 90秒の動画を作成

```bash
python main.py --duration 90
```

### エンターテイメント系の動画を作成

```bash
python main.py --style entertaining
```

### 3本の動画を一度に作成

```bash
python main.py --count 3
```

## 毎日自動実行の設定

### GitHub Actionsを使う場合（推奨）

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」
2. 「New repository secret」をクリック
3. Name: `ANTHROPIC_API_KEY`
4. Value: あなたのAPIキー
5. 保存

これで毎日午前7時に自動実行されます！

### ローカルでCronを使う場合

```bash
# セットアップスクリプトを実行
bash cron-setup.sh

# 表示された指示に従ってcrontabを設定
crontab -e
```

## 次のステップ

- [README.md](README.md) - 詳細なドキュメント
- [config/topics.yaml](config/topics.yaml) - トピックのカスタマイズ
- [templates/vrew_project_template.json](templates/vrew_project_template.json) - テンプレートのカスタマイズ

## トラブルシューティング

### エラー: ANTHROPIC_API_KEY が設定されていません

→ `.env`ファイルを作成して、API Keyを設定してください。

### 動画が生成されない

→ Vrew CLIを使用していない場合は、手動でVrewにファイルをインポートする必要があります。

### トピックが面白くない

→ `config/topics.yaml`を編集して、お好みのトピックを追加してください。

## サポート

質問がある場合は、GitHubのIssuesで報告してください。

楽しい動画作成を！
