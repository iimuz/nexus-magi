"""チャットするためのエントリポイント."""

import sys

from nexus_magi.app import ChatApp


def main() -> int:
    """アプリケーションのエントリポイント.

    Returns:
        int: 終了コード

    """
    app = ChatApp()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
