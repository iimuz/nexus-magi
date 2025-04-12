"""チャットするためのエントリポイント."""

import argparse
import sys

from nexus_magi.app import ChatApp


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析するのだ.

    Returns:
        argparse.Namespace: 解析された引数

    """
    parser = argparse.ArgumentParser(description="ずんだもんとチャットするのだ！")
    parser.add_argument(
        "--provider",
        type=str,
        default="ollama",
        choices=["ollama", "litellm"],
        help="使用するLLMプロバイダー (ollama または litellm) (デフォルト: ollama)"
    )
    parser.add_argument(
        "--api-base",
        type=str,
        help="APIサーバーのベースURL (デフォルト: ollamaの場合はhttp://localhost:11434/api、litellmの場合はhttp://localhost:8000)"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="使用するモデル名 (デフォルト: phi4-mini)"
    )
    return parser.parse_args()


def main() -> int:
    """アプリケーションのエントリポイント.

    Returns:
        int: 終了コード

    """
    args = parse_args()
    app = ChatApp(
        provider=args.provider,
        api_base=args.api_base,
        model=args.model,
    )
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
