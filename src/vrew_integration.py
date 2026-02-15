"""
Vrew Integration Module
Vrewとの連携を行うモジュール
"""

import os
import json
import logging
import subprocess
from datetime import timedelta
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class VrewIntegration:
    """Vrewとの連携を行うクラス"""

    def __init__(
        self,
        vrew_cli_path: Optional[str] = None,
        watch_folder: Optional[str] = None,
        output_folder: Optional[str] = None
    ):
        """
        初期化

        Args:
            vrew_cli_path: Vrew CLIの実行ファイルパス
            watch_folder: Vrewが監視するフォルダパス
            output_folder: 動画出力フォルダパス
        """
        self.vrew_cli_path = vrew_cli_path or os.getenv("VREW_CLI_PATH")
        self.watch_folder = watch_folder or os.getenv("VREW_WATCH_FOLDER", "./output/vrew_projects")
        self.output_folder = output_folder or os.getenv("VREW_OUTPUT_FOLDER", "./output/videos")

        os.makedirs(self.watch_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

    def create_srt_from_script(self, script_data: Dict, output_path: str) -> str:
        """
        スクリプトデータからSRT字幕ファイルを作成

        Args:
            script_data: スクリプトデータ
            output_path: SRTファイルの出力パス

        Returns:
            作成されたSRTファイルのパス
        """
        logger.info(f"SRTファイル作成: {output_path}")

        srt_content = []
        scenes = script_data.get('scenes', [])

        for i, scene in enumerate(scenes, start=1):
            start_time = self._seconds_to_srt_time(scene.get('start_time', 0))
            end_time = self._seconds_to_srt_time(scene.get('end_time', 10))
            subtitle = scene.get('subtitle', scene.get('narration', ''))

            srt_entry = f"{i}\n{start_time} --> {end_time}\n{subtitle}\n"
            srt_content.append(srt_entry)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))

        logger.info(f"SRTファイル作成完了: {len(scenes)}エントリ")
        return output_path

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """秒数をSRT形式の時間に変換 (HH:MM:SS,mmm)"""
        td = timedelta(seconds=seconds)
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        secs = td.seconds % 60
        millis = td.microseconds // 1000

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def create_vrew_project(
        self,
        script_data: Dict,
        project_name: str,
        template_path: Optional[str] = None
    ) -> str:
        """
        Vrewプロジェクトファイルを作成

        Args:
            script_data: スクリプトデータ
            project_name: プロジェクト名
            template_path: テンプレートファイルのパス

        Returns:
            作成されたプロジェクトファイルのパス
        """
        logger.info(f"Vrewプロジェクト作成: {project_name}")

        # テンプレートがあれば読み込む
        if template_path and os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
        else:
            project_data = self._create_default_project_template()

        # スクリプトデータをプロジェクトに反映
        project_data['title'] = script_data.get('title', project_name)
        project_data['description'] = script_data.get('description', '')
        project_data['scenes'] = self._convert_scenes_to_vrew_format(
            script_data.get('scenes', [])
        )

        # プロジェクトファイルを保存
        project_path = os.path.join(self.watch_folder, f"{project_name}.vrew")
        os.makedirs(os.path.dirname(project_path), exist_ok=True)

        with open(project_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Vrewプロジェクト作成完了: {project_path}")
        return project_path

    def _create_default_project_template(self) -> Dict:
        """デフォルトのVrewプロジェクトテンプレートを作成"""
        return {
            "version": "1.0",
            "title": "",
            "description": "",
            "settings": {
                "resolution": {"width": 1920, "height": 1080},
                "fps": 30,
                "audio": {
                    "voice": "auto",
                    "speed": 1.0,
                    "pitch": 1.0
                },
                "style": {
                    "theme": "modern",
                    "font": "default",
                    "text_color": "#FFFFFF",
                    "background_color": "#000000"
                }
            },
            "scenes": []
        }

    def _convert_scenes_to_vrew_format(self, scenes: List[Dict]) -> List[Dict]:
        """スクリプトのシーンをVrew形式に変換"""
        vrew_scenes = []

        for scene in scenes:
            vrew_scene = {
                "scene_id": scene.get('scene_number', len(vrew_scenes) + 1),
                "start_time": scene.get('start_time', 0),
                "duration": scene.get('end_time', 10) - scene.get('start_time', 0),
                "text": scene.get('narration', ''),
                "subtitle": scene.get('subtitle', ''),
                "visual": {
                    "type": "text_overlay",
                    "instructions": scene.get('visual_instructions', '')
                },
                "audio": {
                    "narration": scene.get('narration', ''),
                    "voice_type": "auto"
                }
            }
            vrew_scenes.append(vrew_scene)

        return vrew_scenes

    def export_text_script(self, script_data: Dict, output_path: str) -> str:
        """
        プレーンテキスト形式でスクリプトをエクスポート

        Args:
            script_data: スクリプトデータ
            output_path: 出力ファイルパス

        Returns:
            作成されたファイルのパス
        """
        logger.info(f"テキストスクリプト作成: {output_path}")

        lines = []
        lines.append(f"タイトル: {script_data.get('title', 'Untitled')}")
        lines.append(f"説明: {script_data.get('description', '')}")
        lines.append("")
        lines.append("=" * 60)
        lines.append("")

        for scene in script_data.get('scenes', []):
            scene_num = scene.get('scene_number', 0)
            start = scene.get('start_time', 0)
            end = scene.get('end_time', 0)

            lines.append(f"【シーン {scene_num}】 ({start}秒 - {end}秒)")
            lines.append(f"ナレーション: {scene.get('narration', '')}")
            lines.append(f"字幕: {scene.get('subtitle', '')}")
            lines.append(f"ビジュアル: {scene.get('visual_instructions', '')}")
            lines.append("")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        logger.info(f"テキストスクリプト作成完了: {output_path}")
        return output_path

    def render_video_with_cli(
        self,
        project_path: str,
        output_video_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Vrew CLIを使用して動画をレンダリング

        Args:
            project_path: Vrewプロジェクトファイルのパス
            output_video_path: 出力動画ファイルのパス

        Returns:
            レンダリングされた動画のパス（成功時）
        """
        if not self.vrew_cli_path:
            logger.warning("Vrew CLIパスが設定されていません。手動でVrewを使用してください。")
            return None

        if not os.path.exists(self.vrew_cli_path):
            logger.error(f"Vrew CLIが見つかりません: {self.vrew_cli_path}")
            return None

        if not output_video_path:
            project_name = Path(project_path).stem
            output_video_path = os.path.join(
                self.output_folder,
                f"{project_name}.mp4"
            )

        logger.info(f"動画レンダリング開始: {project_path}")

        try:
            cmd = [
                self.vrew_cli_path,
                "render",
                "--input", project_path,
                "--output", output_video_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                logger.info(f"動画レンダリング完了: {output_video_path}")
                return output_video_path
            else:
                logger.error(f"レンダリングエラー: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("レンダリングタイムアウト（10分）")
            return None
        except Exception as e:
            logger.error(f"レンダリング実行エラー: {e}")
            return None

    def prepare_for_manual_import(
        self,
        script_data: Dict,
        project_name: str
    ) -> Dict[str, str]:
        """
        手動インポート用に各種ファイルを準備

        Args:
            script_data: スクリプトデータ
            project_name: プロジェクト名

        Returns:
            作成されたファイルパスの辞書
        """
        logger.info(f"手動インポート用ファイル準備: {project_name}")

        base_path = os.path.join(self.watch_folder, project_name)
        os.makedirs(base_path, exist_ok=True)

        files = {}

        # SRTファイル
        srt_path = os.path.join(base_path, f"{project_name}.srt")
        files['srt'] = self.create_srt_from_script(script_data, srt_path)

        # テキストスクリプト
        txt_path = os.path.join(base_path, f"{project_name}.txt")
        files['text'] = self.export_text_script(script_data, txt_path)

        # JSONスクリプト
        json_path = os.path.join(base_path, f"{project_name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)
        files['json'] = json_path

        logger.info(f"手動インポート用ファイル準備完了: {len(files)}ファイル")
        return files
