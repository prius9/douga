"""
Topic Selector Module
動画トピックを自動選定するモジュール
"""

import os
import json
import random
import logging
from datetime import datetime
from typing import List, Dict, Optional
import anthropic

logger = logging.getLogger(__name__)


class TopicSelector:
    """トピックを自動選定するクラス"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        topics_config_path: Optional[str] = None,
        use_google_sheets: bool = False,
        google_spreadsheet_id: Optional[str] = None
    ):
        """
        初期化

        Args:
            api_key: Claude API Key
            topics_config_path: トピック設定ファイルのパス
            use_google_sheets: Googleスプレッドシートを使用するか
            google_spreadsheet_id: GoogleスプレッドシートID
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.topics_config_path = topics_config_path or "./config/topics.yaml"
        self.use_google_sheets = use_google_sheets or os.getenv("USE_GOOGLE_SHEETS", "").lower() == "true"
        self.google_spreadsheet_id = google_spreadsheet_id or os.getenv("GOOGLE_SPREADSHEET_ID")

        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = "claude-sonnet-4-5-20250929"
        else:
            self.client = None
            logger.warning("ANTHROPIC_API_KEYが設定されていません。ローカルトピックのみ使用可能です。")

        # Google Sheets連携の初期化
        self.sheets_integration = None
        if self.use_google_sheets:
            try:
                from .google_sheets_integration import GoogleSheetsIntegration
                self.sheets_integration = GoogleSheetsIntegration()
                if self.sheets_integration.is_available():
                    logger.info("Google Sheets連携を有効化しました")
                else:
                    logger.warning("Google Sheets連携の初期化に失敗しました")
            except ImportError:
                logger.warning("Google Sheets連携モジュールが利用できません")

        self.predefined_topics = self._load_predefined_topics()

    def _load_predefined_topics(self) -> List[Dict]:
        """事前定義されたトピックを読み込む"""

        # Googleスプレッドシートから読み込みを試みる
        if self.sheets_integration and self.sheets_integration.is_available() and self.google_spreadsheet_id:
            try:
                logger.info("Googleスプレッドシートからトピックを読み込み中...")
                topics = self.sheets_integration.get_topics_from_sheet(
                    self.google_spreadsheet_id,
                    worksheet_name="Topics"
                )
                if topics:
                    logger.info(f"Googleスプレッドシートから{len(topics)}カテゴリのトピックを読み込みました")
                    return topics
                else:
                    logger.warning("スプレッドシートにトピックがありません。デフォルトを使用します。")
            except Exception as e:
                logger.warning(f"スプレッドシートからの読み込みに失敗: {e}")

        # デフォルトのトピック
        default_topics = [
            {
                "category": "テクノロジー",
                "topics": [
                    "AI技術の最新動向",
                    "プログラミング言語の選び方",
                    "Web開発のベストプラクティス",
                    "クラウドコンピューティング入門",
                    "サイバーセキュリティの基礎"
                ]
            },
            {
                "category": "ビジネス",
                "topics": [
                    "効果的なプレゼンテーション技術",
                    "リモートワークの生産性向上",
                    "スタートアップ起業のステップ",
                    "マーケティング戦略の基本",
                    "ビジネスコミュニケーション術"
                ]
            },
            {
                "category": "教育・学習",
                "topics": [
                    "効率的な学習方法",
                    "記憶力を高めるテクニック",
                    "語学学習のコツ",
                    "オンライン学習の活用法",
                    "クリティカルシンキング入門"
                ]
            },
            {
                "category": "ライフスタイル",
                "topics": [
                    "時間管理術",
                    "ストレス解消法",
                    "健康的な食生活",
                    "ミニマリスト生活のすすめ",
                    "良質な睡眠のための習慣"
                ]
            },
            {
                "category": "クリエイティブ",
                "topics": [
                    "デザインの基本原則",
                    "動画編集のテクニック",
                    "ストーリーテリングの技術",
                    "創造性を高める方法",
                    "コンテンツ制作のアイデア出し"
                ]
            }
        ]

        # 設定ファイルが存在すれば読み込む
        if os.path.exists(self.topics_config_path):
            try:
                import yaml
                with open(self.topics_config_path, 'r', encoding='utf-8') as f:
                    config_topics = yaml.safe_load(f)
                    if config_topics:
                        return config_topics
            except Exception as e:
                logger.warning(f"トピック設定ファイルの読み込みエラー: {e}")

        return default_topics

    def select_random_topic(self) -> str:
        """事前定義されたトピックからランダムに選択"""

        all_topics = []
        for category_data in self.predefined_topics:
            all_topics.extend(category_data.get('topics', []))

        if not all_topics:
            return "今日のおすすめ情報"

        selected = random.choice(all_topics)
        logger.info(f"ランダムトピック選択: {selected}")
        return selected

    def select_topic_by_category(self, category: str) -> str:
        """指定されたカテゴリからトピックを選択"""

        for category_data in self.predefined_topics:
            if category_data.get('category') == category:
                topics = category_data.get('topics', [])
                if topics:
                    selected = random.choice(topics)
                    logger.info(f"カテゴリ'{category}'からトピック選択: {selected}")
                    return selected

        logger.warning(f"カテゴリ'{category}'が見つかりません。ランダム選択します。")
        return self.select_random_topic()

    def generate_trending_topic(self, interests: Optional[List[str]] = None) -> str:
        """
        Claude APIを使用してトレンディングトピックを生成

        Args:
            interests: 興味のある分野のリスト

        Returns:
            生成されたトピック
        """
        if not self.client:
            logger.warning("Claude APIが利用できません。ランダムトピックを使用します。")
            return self.select_random_topic()

        interests_str = ", ".join(interests) if interests else "一般的な話題"

        prompt = f"""あなたは動画コンテンツのトピック提案の専門家です。

以下の条件で、今日作成するべき魅力的な動画トピックを1つ提案してください：

【条件】
- 興味分野: {interests_str}
- ターゲット: 一般視聴者
- 動画の長さ: 60秒程度のショート動画
- トレンド: 2026年2月現在のトレンドを考慮

【要件】
- 視聴者の興味を引く具体的なトピック
- 60秒で説明できる内容
- 教育的または有益な内容
- SEOを意識したキーワードを含む

トピックのタイトルのみを1行で出力してください（説明は不要）。"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            topic = message.content[0].text.strip()
            logger.info(f"トレンディングトピック生成: {topic}")
            return topic

        except Exception as e:
            logger.error(f"トピック生成エラー: {e}")
            return self.select_random_topic()

    def generate_daily_topics(
        self,
        count: int = 1,
        strategy: str = "random",
        **kwargs
    ) -> List[str]:
        """
        毎日のトピックを生成

        Args:
            count: 生成するトピック数
            strategy: 選択戦略 (random, trending, category, sheet)
            **kwargs: 追加パラメータ

        Returns:
            トピックのリスト
        """
        logger.info(f"{count}個のトピックを生成 (戦略: {strategy})")

        topics = []

        for i in range(count):
            if strategy == "sheet":
                # スプレッドシート優先、フォールバックはランダム
                fallback = kwargs.get('fallback_strategy', 'random')
                topic = self.select_topic_with_sheet_priority(fallback)
            elif strategy == "random":
                topic = self.select_random_topic()
            elif strategy == "trending":
                interests = kwargs.get('interests', None)
                topic = self.generate_trending_topic(interests)
            elif strategy == "category":
                category = kwargs.get('category', None)
                if category:
                    topic = self.select_topic_by_category(category)
                else:
                    topic = self.select_random_topic()
            else:
                topic = self.select_random_topic()

            topics.append(topic)

        return topics

    def get_topic_variations(self, base_topic: str, count: int = 3) -> List[str]:
        """
        ベーストピックからバリエーションを生成

        Args:
            base_topic: ベースとなるトピック
            count: 生成するバリエーション数

        Returns:
            トピックバリエーションのリスト
        """
        if not self.client:
            return [base_topic] * count

        prompt = f"""以下のベーストピックから、{count}個のバリエーションを作成してください。
各バリエーションは少しずつ異なる角度や視点から同じテーマを扱います。

ベーストピック: {base_topic}

{count}個のバリエーションを、それぞれ1行ずつ出力してください（番号なし）。"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = message.content[0].text.strip()
            variations = [line.strip() for line in content.split('\n') if line.strip()]
            variations = variations[:count]

            logger.info(f"{len(variations)}個のバリエーション生成完了")
            return variations

        except Exception as e:
            logger.error(f"バリエーション生成エラー: {e}")
            return [base_topic] * count

    def save_daily_topics_log(self, topics: List[str], log_path: str = "./logs/topics_log.json"):
        """
        毎日のトピックをログに保存

        Args:
            topics: 選択されたトピックのリスト
            log_path: ログファイルのパス
        """
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        log_entry = {
            "date": datetime.now().isoformat(),
            "topics": topics
        }

        # 既存のログを読み込む
        logs = []
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except Exception as e:
                logger.warning(f"既存ログの読み込みエラー: {e}")

        # 新しいエントリを追加
        logs.append(log_entry)

        # ログを保存（最新100件のみ保持）
        logs = logs[-100:]

        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

        logger.info(f"トピックログ保存完了: {log_path}")

    def get_available_categories(self) -> List[str]:
        """利用可能なカテゴリの一覧を取得"""
        return [cat.get('category', '') for cat in self.predefined_topics]

    def get_today_topic_from_sheet(self) -> Optional[str]:
        """
        Googleスプレッドシートから今日のトピックを取得

        Returns:
            今日のトピック（見つからない場合はNone）
        """
        if not self.sheets_integration or not self.google_spreadsheet_id:
            return None

        try:
            today_entry = self.sheets_integration.get_today_topic(
                self.google_spreadsheet_id,
                worksheet_name="Schedule"
            )

            if today_entry:
                topic = today_entry.get('topic', '')
                logger.info(f"スプレッドシートから今日のトピックを取得: {topic}")
                return topic

            return None

        except Exception as e:
            logger.error(f"今日のトピック取得エラー: {e}")
            return None

    def select_topic_with_sheet_priority(self, fallback_strategy: str = "random") -> str:
        """
        スプレッドシート優先でトピックを選択

        まずスプレッドシートから今日のトピックを取得し、
        見つからない場合は指定された戦略でフォールバック

        Args:
            fallback_strategy: フォールバック時の選択戦略

        Returns:
            選択されたトピック
        """
        # まずスプレッドシートから取得を試みる
        topic = self.get_today_topic_from_sheet()

        if topic:
            return topic

        # フォールバック
        logger.info(f"スプレッドシートにトピックがないため、{fallback_strategy}戦略で選択")

        if fallback_strategy == "trending":
            return self.generate_trending_topic()
        elif fallback_strategy == "random":
            return self.select_random_topic()
        else:
            return self.select_random_topic()
