#!/bin/bash
#
# Cron設定スクリプト
# 毎日自動実行するためのcrontab設定を行います
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

# ログディレクトリの作成
mkdir -p "$LOG_DIR"

# Cron用の実行スクリプトを作成
cat > "$SCRIPT_DIR/run-daily-video.sh" << 'EOF'
#!/bin/bash

# プロジェクトディレクトリに移動
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 環境変数の読み込み
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Pythonの仮想環境がある場合はアクティベート
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# ログファイルのパス
LOG_FILE="logs/cron_$(date +%Y%m%d).log"

# 動画生成の実行
echo "========================================" >> "$LOG_FILE"
echo "実行開始: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

python main.py --topic-strategy random --log-level INFO >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

echo "========================================" >> "$LOG_FILE"
echo "実行終了: $(date) (終了コード: $EXIT_CODE)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 古いログファイルを削除（30日以上前）
find logs/ -name "cron_*.log" -mtime +30 -delete

exit $EXIT_CODE
EOF

chmod +x "$SCRIPT_DIR/run-daily-video.sh"

echo "✓ 実行スクリプト作成完了: run-daily-video.sh"
echo ""

# Crontab設定例を表示
cat << EOF
========================================
Crontab設定例
========================================

以下のコマンドでcrontabを編集してください:

    crontab -e

そして、以下の行を追加します:

# 毎日午前7時に動画生成を実行
0 7 * * * $SCRIPT_DIR/run-daily-video.sh

# または、毎日午前7時、午後3時、午後10時に実行
0 7,15,22 * * * $SCRIPT_DIR/run-daily-video.sh

========================================
環境変数の設定
========================================

$SCRIPT_DIR/.env ファイルに以下を設定してください:

ANTHROPIC_API_KEY=your_api_key_here
VREW_CLI_PATH=/path/to/vrew/cli
VREW_WATCH_FOLDER=$SCRIPT_DIR/output/vrew_projects
VREW_OUTPUT_FOLDER=$SCRIPT_DIR/output/videos

========================================
動作確認
========================================

以下のコマンドで手動実行して動作確認できます:

    $SCRIPT_DIR/run-daily-video.sh

ログは以下のファイルに出力されます:

    $LOG_DIR/cron_$(date +%Y%m%d).log

========================================
EOF
