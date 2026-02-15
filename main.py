#!/usr/bin/env python3
"""
Claude to Vrew Video Generation - Main Script
毎日自動実行されるメインスクリプト
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.video_pipeline import VideoPipeline


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """ロギングの設定"""

    # ログレベルの設定
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    # ログフォーマット
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # ハンドラーの設定
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))

    # ロギング設定
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )


def main():
    """メイン処理"""

    # コマンドライン引数のパース
    parser = argparse.ArgumentParser(
        description='Claude to Vrew 自動動画生成システム'
    )
    parser.add_argument(
        '--topic',
        type=str,
        help='動画のトピック（指定しない場合は自動選択）'
    )
    parser.add_argument(
        '--topic-strategy',
        type=str,
        default='random',
        choices=['random', 'trending', 'category', 'sheet'],
        help='トピック選択戦略（sheet: Googleスプレッドシートから取得）'
    )
    parser.add_argument(
        '--category',
        type=str,
        help='カテゴリを指定（topic-strategy=categoryの場合）'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='動画の長さ（秒）'
    )
    parser.add_argument(
        '--style',
        type=str,
        default='informative',
        choices=['informative', 'entertaining', 'educational'],
        help='動画のスタイル'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='生成する動画の数'
    )
    parser.add_argument(
        '--auto-render',
        action='store_true',
        help='自動でVrewレンダリングを実行'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='ログレベル'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./output',
        help='出力ディレクトリ'
    )

    args = parser.parse_args()

    # ロギングの設定
    log_file = f"./logs/video_generation_{datetime.now().strftime('%Y%m%d')}.log"
    setup_logging(args.log_level, log_file)

    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("Claude to Vrew 自動動画生成システム 起動")
    logger.info("=" * 80)
    logger.info(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"トピック戦略: {args.topic_strategy}")
    logger.info(f"動画数: {args.count}")
    logger.info(f"動画の長さ: {args.duration}秒")
    logger.info(f"スタイル: {args.style}")
    logger.info("=" * 80)

    try:
        # API Keyの確認
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY が設定されていません！")
            logger.error("環境変数またはdotenvファイルでAPIキーを設定してください。")
            sys.exit(1)

        # パイプラインの初期化
        pipeline = VideoPipeline(
            api_key=api_key,
            vrew_cli_path=os.getenv("VREW_CLI_PATH"),
            output_base_path=args.output_dir
        )

        # 動画生成の実行
        if args.count == 1:
            # 1本の動画を生成
            result = pipeline.generate_daily_video(
                topic=args.topic,
                topic_strategy=args.topic_strategy,
                duration=args.duration,
                style=args.style,
                auto_render=args.auto_render
            )

            # 結果の表示
            summary = pipeline.get_generation_summary(result)
            print("\n" + summary)

            # ログに保存
            pipeline.save_result_log(result)

            # 終了コード
            sys.exit(0 if result['success'] else 1)

        else:
            # 複数の動画を生成
            kwargs = {
                'topic_strategy': args.topic_strategy,
                'duration': args.duration,
                'style': args.style,
                'auto_render': args.auto_render
            }

            results = pipeline.generate_multiple_videos(
                count=args.count,
                **kwargs
            )

            # 結果の表示
            for i, result in enumerate(results, start=1):
                summary = pipeline.get_generation_summary(result)
                print(f"\n動画 {i}/{args.count}:")
                print(summary)
                pipeline.save_result_log(result)

            # 成功数の集計
            success_count = sum(1 for r in results if r['success'])
            logger.info(f"\n総合結果: {success_count}/{args.count} 本成功")

            # 終了コード
            sys.exit(0 if success_count == args.count else 1)

    except KeyboardInterrupt:
        logger.info("\n処理が中断されました")
        sys.exit(130)

    except Exception as e:
        logger.exception(f"予期しないエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
