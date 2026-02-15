"""
Google Sheets Integration Module
Googleスプレッドシートから動画コンテンツ情報を取得するモジュール
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class GoogleSheetsIntegration:
    """Googleスプレッドシートとの連携クラス"""

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        use_service_account: bool = True
    ):
        """
        初期化

        Args:
            credentials_path: 認証情報ファイルのパス
            use_service_account: サービスアカウントを使用するか
        """
        self.credentials_path = credentials_path or os.getenv(
            "GOOGLE_CREDENTIALS_PATH",
            "./config/google_credentials.json"
        )
        self.use_service_account = use_service_account
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Google Sheets APIクライアントを初期化"""
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            if not os.path.exists(self.credentials_path):
                logger.warning(
                    f"認証情報ファイルが見つかりません: {self.credentials_path}"
                )
                logger.warning("Googleスプレッドシート機能は利用できません")
                return

            # スコープの設定
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]

            # 認証
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scopes
            )

            # クライアント初期化
            self.client = gspread.authorize(credentials)
            logger.info("Google Sheetsクライアント初期化完了")

        except ImportError:
            logger.warning(
                "gspreadライブラリがインストールされていません。"
                "pip install gspread google-auth を実行してください。"
            )
        except Exception as e:
            logger.error(f"Google Sheetsクライアント初期化エラー: {e}")

    def get_topics_from_sheet(
        self,
        spreadsheet_id: str,
        worksheet_name: str = "Topics",
        category_column: str = "A",
        topic_column: str = "B"
    ) -> List[Dict]:
        """
        スプレッドシートからトピック一覧を取得

        スプレッドシート形式例:
        | Category    | Topic                  |
        |-------------|------------------------|
        | テクノロジー | AI技術の最新動向        |
        | ビジネス     | リモートワークのコツ    |

        Args:
            spreadsheet_id: スプレッドシートID
            worksheet_name: ワークシート名
            category_column: カテゴリ列（A, B, C...）
            topic_column: トピック列（A, B, C...）

        Returns:
            トピック情報の辞書リスト
        """
        if not self.client:
            logger.error("Google Sheetsクライアントが初期化されていません")
            return []

        try:
            # スプレッドシートを開く
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)

            # データを取得
            all_values = worksheet.get_all_values()

            if not all_values or len(all_values) < 2:
                logger.warning("スプレッドシートにデータがありません")
                return []

            # ヘッダー行をスキップ
            data_rows = all_values[1:]

            # カテゴリごとにグループ化
            topics_by_category = {}

            for row in data_rows:
                if len(row) < 2:
                    continue

                category = row[0].strip()
                topic = row[1].strip()

                if not category or not topic:
                    continue

                if category not in topics_by_category:
                    topics_by_category[category] = []

                topics_by_category[category].append(topic)

            # 結果を整形
            result = []
            for category, topics in topics_by_category.items():
                result.append({
                    "category": category,
                    "topics": topics
                })

            logger.info(
                f"スプレッドシートから{len(result)}カテゴリ、"
                f"{sum(len(t['topics']) for t in result)}トピックを取得"
            )

            return result

        except Exception as e:
            logger.error(f"スプレッドシートからのデータ取得エラー: {e}")
            return []

    def get_daily_schedule_from_sheet(
        self,
        spreadsheet_id: str,
        worksheet_name: str = "Schedule"
    ) -> List[Dict]:
        """
        スプレッドシートから毎日のスケジュールを取得

        スプレッドシート形式例:
        | Date       | Topic              | Duration | Style       | Notes        |
        |------------|--------------------|----------|-------------|--------------|
        | 2026-02-15 | AI技術の最新動向    | 60       | informative | トレンド重視 |

        Args:
            spreadsheet_id: スプレッドシートID
            worksheet_name: ワークシート名

        Returns:
            スケジュール情報の辞書リスト
        """
        if not self.client:
            logger.error("Google Sheetsクライアントが初期化されていません")
            return []

        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)

            # データを取得
            all_values = worksheet.get_all_values()

            if not all_values or len(all_values) < 2:
                logger.warning("スケジュールデータがありません")
                return []

            # ヘッダー行
            headers = [h.lower().strip() for h in all_values[0]]
            data_rows = all_values[1:]

            schedule = []

            for row in data_rows:
                if len(row) < len(headers):
                    # 不足している列を空文字で埋める
                    row.extend([''] * (len(headers) - len(row)))

                entry = {}
                for i, header in enumerate(headers):
                    entry[header] = row[i].strip()

                # 必須フィールドのチェック
                if entry.get('date') and entry.get('topic'):
                    schedule.append(entry)

            logger.info(f"スケジュールを{len(schedule)}件取得")
            return schedule

        except Exception as e:
            logger.error(f"スケジュール取得エラー: {e}")
            return []

    def get_today_topic(
        self,
        spreadsheet_id: str,
        worksheet_name: str = "Schedule"
    ) -> Optional[Dict]:
        """
        今日のトピックをスプレッドシートから取得

        Args:
            spreadsheet_id: スプレッドシートID
            worksheet_name: ワークシート名

        Returns:
            今日のトピック情報（見つからない場合はNone）
        """
        schedule = self.get_daily_schedule_from_sheet(
            spreadsheet_id,
            worksheet_name
        )

        if not schedule:
            return None

        today = datetime.now().strftime("%Y-%m-%d")

        for entry in schedule:
            entry_date = entry.get('date', '').strip()

            # 日付フォーマットの正規化
            try:
                # YYYY-MM-DD形式に変換
                if '/' in entry_date:
                    parts = entry_date.split('/')
                    if len(parts) == 3:
                        entry_date = f"{parts[0]}-{parts[1]:0>2}-{parts[2]:0>2}"
            except:
                pass

            if entry_date == today:
                logger.info(f"今日のトピックを発見: {entry.get('topic')}")
                return entry

        logger.info("今日のスケジュールが見つかりませんでした")
        return None

    def get_content_template_from_sheet(
        self,
        spreadsheet_id: str,
        worksheet_name: str = "Templates",
        template_name: str = "default"
    ) -> Optional[Dict]:
        """
        スプレッドシートからコンテンツテンプレートを取得

        スプレッドシート形式例:
        | Template Name | Opening        | Main Content Style | Closing         |
        |---------------|----------------|-------------------|-----------------|
        | default       | こんにちは！   | 箇条書き3点       | ありがとう！    |

        Args:
            spreadsheet_id: スプレッドシートID
            worksheet_name: ワークシート名
            template_name: テンプレート名

        Returns:
            テンプレート情報
        """
        if not self.client:
            return None

        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)

            all_values = worksheet.get_all_values()

            if not all_values or len(all_values) < 2:
                return None

            headers = [h.lower().strip() for h in all_values[0]]
            data_rows = all_values[1:]

            for row in data_rows:
                if len(row) == 0:
                    continue

                name = row[0].strip()
                if name == template_name:
                    template = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            template[header] = row[i].strip()
                    return template

            return None

        except Exception as e:
            logger.error(f"テンプレート取得エラー: {e}")
            return None

    def update_generation_log(
        self,
        spreadsheet_id: str,
        worksheet_name: str = "GenerationLog",
        log_entry: Dict[str, Any] = None
    ) -> bool:
        """
        生成ログをスプレッドシートに記録

        Args:
            spreadsheet_id: スプレッドシートID
            worksheet_name: ワークシート名
            log_entry: ログエントリ

        Returns:
            成功したかどうか
        """
        if not self.client or not log_entry:
            return False

        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)

            # ワークシートを取得または作成
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
            except:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=1000,
                    cols=10
                )
                # ヘッダー行を追加
                worksheet.append_row([
                    "Timestamp",
                    "Topic",
                    "Duration",
                    "Style",
                    "Success",
                    "Script Path",
                    "Video Path",
                    "Notes"
                ])

            # ログエントリを追加
            row = [
                log_entry.get('timestamp', datetime.now().isoformat()),
                log_entry.get('topic', ''),
                log_entry.get('duration', ''),
                log_entry.get('style', ''),
                log_entry.get('success', False),
                log_entry.get('script_path', ''),
                log_entry.get('video_path', ''),
                log_entry.get('notes', '')
            ]

            worksheet.append_row(row)
            logger.info("生成ログをスプレッドシートに記録しました")
            return True

        except Exception as e:
            logger.error(f"ログ記録エラー: {e}")
            return False

    def is_available(self) -> bool:
        """Google Sheets機能が利用可能かどうか"""
        return self.client is not None
