"""
Video Generation Pipeline
動画生成の全体パイプラインを管理するモジュール
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from .claude_script_generator import ClaudeScriptGenerator
from .vrew_integration import VrewIntegration
from .topic_selector import TopicSelector

logger = logging.getLogger(__name__)


class VideoPipeline:
    """動画生成パイプラインを管理するクラス"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        vrew_cli_path: Optional[str] = None,
        output_base_path: str = "./output"
    ):
        """
        初期化

        Args:
            api_key: Claude API Key
            vrew_cli_path: Vrew CLIのパス
            output_base_path: 出力ベースディレクトリ
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.output_base_path = output_base_path

        # 各モジュールを初期化
        self.topic_selector = TopicSelector(api_key=self.api_key)
        self.script_generator = ClaudeScriptGenerator(api_key=self.api_key)
        self.vrew_integration = VrewIntegration(
            vrew_cli_path=vrew_cli_path,
            watch_folder=os.path.join(output_base_path, "vrew_projects"),
            output_folder=os.path.join(output_base_path, "videos")
        )

        # 出力ディレクトリを作成
        self._setup_directories()

        logger.info("動画パイプライン初期化完了")

    def _setup_directories(self):
        """必要なディレクトリを作成"""
        directories = [
            os.path.join(self.output_base_path, "scripts"),
            os.path.join(self.output_base_path, "vrew_projects"),
            os.path.join(self.output_base_path, "videos"),
            "./logs"
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def generate_daily_video(
        self,
        topic: Optional[str] = None,
        topic_strategy: str = "random",
        duration: int = 60,
        style: str = "informative",
        auto_render: bool = False
    ) -> Dict:
        """
        1日1本の動画を自動生成

        Args:
            topic: トピック（指定しない場合は自動選択）
            topic_strategy: トピック選択戦略
            duration: 動画の長さ（秒）
            style: 動画のスタイル
            auto_render: 自動でレンダリングするか

        Returns:
            生成結果の辞書
        """
        logger.info("=" * 60)
        logger.info("動画生成パイプライン開始")
        logger.info("=" * 60)

        result = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "topic": None,
            "script_path": None,
            "vrew_files": None,
            "video_path": None,
            "errors": []
        }

        try:
            # ステップ1: トピック選択
            if not topic:
                logger.info("ステップ1: トピック自動選択")
                topics = self.topic_selector.generate_daily_topics(
                    count=1,
                    strategy=topic_strategy
                )
                topic = topics[0]
                self.topic_selector.save_daily_topics_log(topics)
            else:
                logger.info(f"ステップ1: 指定されたトピック: {topic}")

            result["topic"] = topic

            # ステップ2: スクリプト生成
            logger.info("ステップ2: スクリプト生成")
            script_data = self.script_generator.generate_script(
                topic=topic,
                duration_seconds=duration,
                style=style
            )

            # スクリプトを保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script_filename = f"script_{timestamp}.json"
            script_path = os.path.join(
                self.output_base_path,
                "scripts",
                script_filename
            )
            self.script_generator.save_script(script_data, script_path)
            result["script_path"] = script_path

            # ステップ3: Vrew用ファイル生成
            logger.info("ステップ3: Vrew用ファイル生成")
            project_name = f"video_{timestamp}"
            vrew_files = self.vrew_integration.prepare_for_manual_import(
                script_data,
                project_name
            )
            result["vrew_files"] = vrew_files

            # オプション: Vrewプロジェクトファイルも作成
            vrew_project_path = self.vrew_integration.create_vrew_project(
                script_data,
                project_name
            )
            vrew_files["vrew_project"] = vrew_project_path

            # ステップ4: 自動レンダリング（オプション）
            if auto_render and self.vrew_integration.vrew_cli_path:
                logger.info("ステップ4: 動画レンダリング")
                video_path = self.vrew_integration.render_video_with_cli(
                    vrew_project_path
                )
                result["video_path"] = video_path
            else:
                logger.info("ステップ4: スキップ（手動レンダリング）")
                logger.info(f"Vrewプロジェクト: {vrew_project_path}")

            result["success"] = True
            logger.info("=" * 60)
            logger.info("動画生成パイプライン完了")
            logger.info("=" * 60)

        except Exception as e:
            error_msg = f"パイプラインエラー: {e}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    def generate_multiple_videos(
        self,
        count: int = 3,
        **kwargs
    ) -> List[Dict]:
        """
        複数の動画を一括生成

        Args:
            count: 生成する動画の数
            **kwargs: generate_daily_videoに渡すパラメータ

        Returns:
            生成結果のリスト
        """
        logger.info(f"{count}本の動画を一括生成")

        results = []
        for i in range(count):
            logger.info(f"動画 {i + 1}/{count} を生成")
            result = self.generate_daily_video(**kwargs)
            results.append(result)

        success_count = sum(1 for r in results if r["success"])
        logger.info(f"一括生成完了: {success_count}/{count} 成功")

        return results

    def get_generation_summary(self, result: Dict) -> str:
        """
        生成結果のサマリーを取得

        Args:
            result: 生成結果の辞書

        Returns:
            サマリー文字列
        """
        lines = []
        lines.append("=" * 60)
        lines.append("動画生成結果サマリー")
        lines.append("=" * 60)
        lines.append(f"成功: {'はい' if result['success'] else 'いいえ'}")
        lines.append(f"タイムスタンプ: {result['timestamp']}")
        lines.append(f"トピック: {result['topic']}")

        if result['script_path']:
            lines.append(f"スクリプト: {result['script_path']}")

        if result['vrew_files']:
            lines.append("Vrewファイル:")
            for file_type, file_path in result['vrew_files'].items():
                lines.append(f"  - {file_type}: {file_path}")

        if result['video_path']:
            lines.append(f"動画: {result['video_path']}")

        if result['errors']:
            lines.append("エラー:")
            for error in result['errors']:
                lines.append(f"  - {error}")

        lines.append("=" * 60)

        return "\n".join(lines)

    def save_result_log(
        self,
        result: Dict,
        log_path: str = "./logs/generation_log.json"
    ):
        """
        生成結果をログに保存

        Args:
            result: 生成結果の辞書
            log_path: ログファイルのパス
        """
        import json

        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # 既存のログを読み込む
        logs = []
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except Exception as e:
                logger.warning(f"既存ログの読み込みエラー: {e}")

        # 新しいエントリを追加
        logs.append(result)

        # ログを保存（最新100件のみ保持）
        logs = logs[-100:]

        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

        logger.info(f"生成ログ保存完了: {log_path}")
