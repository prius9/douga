# Claude to Vrew 自動動画生成システム - Windows起動スクリプト
# 使い方: PowerShellで以下を実行
#   .\start.ps1
#   .\start.ps1 -Topic "AI技術の最新動向"
#   .\start.ps1 -Strategy sheet
#   .\start.ps1 -Count 3 -Duration 90

param(
    [string]$Topic = "",
    [string]$Strategy = "sheet",
    [string]$Category = "",
    [int]$Count = 1,
    [int]$Duration = 60,
    [string]$Style = "informative",
    [switch]$AutoRender
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# スクリプトのディレクトリに移動
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "=== Claude to Vrew 自動動画生成 ===" -ForegroundColor Cyan

# .envファイルの読み込み
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
    Write-Host "✓ .envを読み込みました" -ForegroundColor Green
} else {
    Write-Host "⚠ .envが見つかりません。.env.exampleをコピーして設定してください。" -ForegroundColor Yellow
    Write-Host "  コマンド: Copy-Item .env.example .env" -ForegroundColor Yellow
    exit 1
}

# ANTHROPIC_API_KEYの確認
if (-not $env:ANTHROPIC_API_KEY) {
    Write-Host "✗ ANTHROPIC_API_KEYが設定されていません。.envを確認してください。" -ForegroundColor Red
    exit 1
}
Write-Host "✓ API Key確認済み" -ForegroundColor Green

# Python確認
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Pythonが見つかりません。インストールしてください。" -ForegroundColor Red
    exit 1
}

# 仮想環境の確認・アクティベート
if (Test-Path "venv\Scripts\Activate.ps1") {
    . "venv\Scripts\Activate.ps1"
    Write-Host "✓ 仮想環境を有効化しました" -ForegroundColor Green
} elseif (-not (python -c "import anthropic" 2>$null)) {
    Write-Host "依存関係をインストール中..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet
    Write-Host "✓ インストール完了" -ForegroundColor Green
}

# 引数を組み立て
$args_list = @()

if ($Topic)    { $args_list += "--topic", $Topic }
$args_list += "--topic-strategy", $Strategy
if ($Category) { $args_list += "--category", $Category }
$args_list += "--count", $Count
$args_list += "--duration", $Duration
$args_list += "--style", $Style
if ($AutoRender) { $args_list += "--auto-render" }

Write-Host ""
Write-Host "実行中..." -ForegroundColor Cyan
python main.py @args_list
