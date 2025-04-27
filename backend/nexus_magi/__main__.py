"""チャットAPIサーバーのエントリポイント."""

import argparse
import sys

from nexus_magi.app import run_app


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析するのだ.

    Returns:
        argparse.Namespace: 解析された引数

    """
    parser = argparse.ArgumentParser(description="MAGI合議システムAPIサーバー")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="サーバーのホスト (デフォルト: 127.0.0.1)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="サーバーのポート (デフォルト: 8000)"
    )
    parser.add_argument(
        "--api-type",
        type=str,
        default="ollama",
        choices=["ollama", "litellm"],
        help="使用するLLM APIの種類 (ollama または litellm) (デフォルト: ollama)",
    )
    parser.add_argument(
        "--api-base",
        type=str,
        help="LLM APIのベースURL (デフォルト: ollamaの場合はhttp://localhost:11434/api、litellmの場合はhttp://localhost:4000)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="phi4-mini",
        help="使用するモデル名 (デフォルト: phi4-mini)",
    )
    return parser.parse_args()


def main() -> int:
    """アプリケーションのエントリポイント.

    Returns:
        int: 終了コード

    """
    args = parse_args()
    run_app(
        host=args.host,
        port=args.port,
        api_base=args.api_base,
        model=args.model,
        api_type=args.api_type,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
