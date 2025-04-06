"""チャットアプリケーションのメインクラスを定義."""

from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, Static

from nexus_magi.chat_model import ChatModel


class Message(Static):
    """チャットメッセージを表示するウィジェット."""

    DEFAULT_CSS = """
    Message {
        width: 100%;
        padding: 0 1;
        margin: 0 0;
    }
    .user {
        color: #00FF00;
    }
    .assistant {
        color: #FFFFFF;
    }
    """

    def __init__(self, message: str, role: str, **kwargs: Any) -> None:
        """メッセージウィジェットを初期化する。

        Args:
            message: 表示するメッセージ
            role: メッセージの送信者（user または assistant）
            **kwargs: その他の引数

        """
        super().__init__(message, **kwargs)
        self.add_class(role)


class MessageArea(Vertical):
    """メッセージエリアを表示するコンテナ."""

    DEFAULT_CSS = """
    MessageArea {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
        background: #1a1a1a;
    }
    """


class ChatArea(Container):
    """チャットエリア全体を管理するコンテナ."""

    DEFAULT_CSS = """
    ChatArea {
        layout: vertical;
        width: 100%;
        height: 100%;
    }

    #input-area {
        width: 100%;
        height: auto;
        background: #333333;
        padding: 1 1;
        align: center middle;
    }

    #message-input {
        width: 1fr;
    }
    """

    messages = reactive([])

    def __init__(self, **kwargs: Any) -> None:
        """チャットエリアを初期化.

        Args:
            **kwargs: その他の引数

        """
        super().__init__(**kwargs)
        self.chat_model = ChatModel()

    def compose(self) -> ComposeResult:
        """UIコンポーネントを構成.

        Returns:
            ComposeResult: コンポーネントの構成結果

        """
        with MessageArea(id="message-area"):
            # メッセージは動的に追加されるのだ
            pass

        with Horizontal(id="input-area"):
            yield Input(placeholder="メッセージを入力するのだ...", id="message-input")

    def on_mount(self) -> None:
        """コンポーネントがマウントされたときの処理."""
        self.query_one("#message-input").focus()

        # 初期メッセージを表示するのだ
        self.add_message("こんにちは！ぼくはずんだもんなのだ。どうしたのだ？", "assistant")

    def add_message(self, message: str, role: str) -> None:
        """新しいメッセージを追加する.

        Args:
            message: メッセージの内容
            role: メッセージの送信者(user または assistant)

        """
        self.messages.append({"role": role, "content": message})
        message_area = self.query_one("#message-area")
        message_area.mount(Message(message, role))
        message_area.scroll_end()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """入力が送信されたときの処理.

        Args:
            event: 入力送信イベント

        """
        if event.input.id == "message-input":
            self.run_worker(self.send_message())

    async def send_message(self) -> None:
        """メッセージを送信する."""
        input_widget = self.query_one("#message-input", Input)
        message = input_widget.value

        if not message:
            return

        # ユーザーメッセージを表示するのだ
        self.add_message(message, "user")

        # 入力欄をクリアするのだ
        input_widget.value = ""

        # LLMからの応答を取得するのだ
        await self.get_ai_response(message)

    async def get_ai_response(self, user_message: str) -> None:
        """AIからの応答を取得して表示.

        Args:
            user_message: ユーザーが入力したメッセージ

        """
        # 「考え中...」メッセージを表示するのだ
        thinking_message = Message("考え中なのだ...", "assistant")
        message_area = self.query_one("#message-area")
        message_area.mount(thinking_message)
        message_area.scroll_end()

        # AIからの応答を取得するのだ
        response = await self.chat_model.get_response(self.messages)

        # 「考え中...」メッセージを削除するのだ
        thinking_message.remove()

        # 応答を表示するのだ
        self.add_message(response, "assistant")


class ChatApp(App):
    """チャットアプリケーションのメインクラス."""

    TITLE = "ずんだもんとチャット"
    CSS = """
    Screen {
        background: #121212;
    }
    """

    def compose(self) -> ComposeResult:
        """UIコンポーネントを構成.

        Returns:
            ComposeResult: コンポーネントの構成結果

        """
        yield Header()
        yield ChatArea()
        yield Footer()
