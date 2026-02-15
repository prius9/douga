"""
Claude API Script Generator
Claude APIを使用して動画スクリプトを自動生成するモジュール
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import anthropic

logger = logging.getLogger(__name__)


class ClaudeScriptGenerator:
    """Claude APIを使用してスクリプトを生成するクラス"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: Claude API Key (指定しない場合は環境変数から取得)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def generate_script(
        self,
        topic: str,
        duration_seconds: int = 60,
        style: str = "informative",
        target_audience: str = "general"
    ) -> Dict:
        """
        指定されたトピックに基づいて動画スクリプトを生成

        Args:
            topic: 動画のトピック
            duration_seconds: 動画の長さ（秒）
            style: 動画のスタイル (informative, entertaining, educational, etc.)
            target_audience: ターゲット視聴者層

        Returns:
            スクリプト情報を含む辞書
        """
        logger.info(f"スクリプト生成開始: トピック='{topic}', 長さ={duration_seconds}秒")

        prompt = self._create_prompt(topic, duration_seconds, style, target_audience)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = message.content[0].text
            script_data = self._parse_script_response(content, topic)

            logger.info(f"スクリプト生成完了: {len(script_data['scenes'])}シーン")
            return script_data

        except Exception as e:
            logger.error(f"スクリプト生成エラー: {e}")
            raise

    def _create_prompt(
        self,
        topic: str,
        duration_seconds: int,
        style: str,
        target_audience: str
    ) -> str:
        """スクリプト生成用のプロンプトを作成"""

        return f"""あなたはプロの動画スクリプトライターです。以下の条件で動画スクリプトを作成してください。

【条件】
- トピック: {topic}
- 動画の長さ: 約{duration_seconds}秒
- スタイル: {style}
- ターゲット視聴者: {target_audience}

【要件】
1. 視聴者の興味を引く魅力的なオープニング
2. 明確な構成（導入・本論・結論）
3. 各シーンごとにナレーション原稿とタイムスタンプ
4. 視覚的な指示（画面に表示する内容の提案）
5. 字幕として表示するテキスト

【出力形式】
以下のJSON形式で出力してください：

{{
  "title": "動画のタイトル",
  "description": "動画の説明",
  "total_duration": {duration_seconds},
  "scenes": [
    {{
      "scene_number": 1,
      "start_time": 0,
      "end_time": 10,
      "narration": "ナレーション原稿",
      "subtitle": "字幕テキスト",
      "visual_instructions": "画面表示の指示"
    }}
  ],
  "keywords": ["キーワード1", "キーワード2"],
  "hashtags": ["#ハッシュタグ1", "#ハッシュタグ2"]
}}

それでは、魅力的な動画スクリプトを作成してください。"""

    def _parse_script_response(self, response: str, topic: str) -> Dict:
        """Claude APIのレスポンスをパースしてスクリプトデータに変換"""

        try:
            # JSONブロックを抽出
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("JSONデータが見つかりません")

            json_str = response[start_idx:end_idx]
            script_data = json.loads(json_str)

            # メタデータを追加
            script_data['generated_at'] = datetime.now().isoformat()
            script_data['topic'] = topic

            return script_data

        except json.JSONDecodeError as e:
            logger.error(f"JSONパースエラー: {e}")
            # フォールバックとして基本的なスクリプトを返す
            return self._create_fallback_script(topic, response)

    def _create_fallback_script(self, topic: str, content: str) -> Dict:
        """パースに失敗した場合のフォールバックスクリプト"""

        return {
            "title": topic,
            "description": f"{topic}についての動画",
            "total_duration": 60,
            "scenes": [
                {
                    "scene_number": 1,
                    "start_time": 0,
                    "end_time": 60,
                    "narration": content[:500],
                    "subtitle": content[:200],
                    "visual_instructions": "トピックに関連する画像を表示"
                }
            ],
            "keywords": [topic],
            "hashtags": [f"#{topic}"],
            "generated_at": datetime.now().isoformat(),
            "topic": topic
        }

    def generate_multiple_scripts(
        self,
        topics: List[str],
        **kwargs
    ) -> List[Dict]:
        """
        複数のトピックに対してスクリプトを一括生成

        Args:
            topics: トピックのリスト
            **kwargs: generate_scriptに渡す追加パラメータ

        Returns:
            スクリプトデータのリスト
        """
        scripts = []

        for topic in topics:
            try:
                script = self.generate_script(topic, **kwargs)
                scripts.append(script)
            except Exception as e:
                logger.error(f"トピック'{topic}'のスクリプト生成失敗: {e}")
                continue

        return scripts

    def save_script(self, script_data: Dict, output_path: str) -> str:
        """
        スクリプトをファイルに保存

        Args:
            script_data: スクリプトデータ
            output_path: 出力先パス

        Returns:
            保存されたファイルパス
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)

        logger.info(f"スクリプト保存完了: {output_path}")
        return output_path
