#!/bin/bash
set -euo pipefail

# リモート環境（Claude Code on the web）でのみ実行
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "=== Claude to Vrew - セッション初期化 ==="

# Python依存関係のインストール
echo "Pythonパッケージをインストール中..."
pip install -r "$CLAUDE_PROJECT_DIR/requirements.txt" --quiet

# 必要なディレクトリの作成
echo "出力ディレクトリを作成中..."
mkdir -p "$CLAUDE_PROJECT_DIR/output/scripts"
mkdir -p "$CLAUDE_PROJECT_DIR/output/videos"
mkdir -p "$CLAUDE_PROJECT_DIR/output/vrew_projects"
mkdir -p "$CLAUDE_PROJECT_DIR/logs"

# PYTHONPATHの設定
echo "export PYTHONPATH=\"$CLAUDE_PROJECT_DIR\"" >> "$CLAUDE_ENV_FILE"

echo "=== 初期化完了 ==="
