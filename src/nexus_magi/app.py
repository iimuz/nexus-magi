"""チャットアプリケーションのメインクラスを定義."""

from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, Static

from nexus_magi.chat_model import ChatModel


def escape_markup(text: str) -> str:
    """マークアップ文字をエスケープする.

    Args:
        text: エスケープするテキスト

    Returns:
        str: エスケープされたテキスト

    """
    # '[' と ']' をエスケープして、マークアップとして解釈されないようにする
    return text.replace("[", "\\[").replace("]", "\\]")


class Message(Static):
    """チャットメッセージを表示するウィジェット."""

    DEFAULT_CSS = """
    Message {
        width: 100%;
        padding: 1 1;
        margin: 1 0;
        border: solid #333333;
        border-top: none;
        border-right: none;
        border-bottom: solid #333333;
        border-left: none;
    }
    .user {
        color: #00FF00;
        background: #1e3a1e;
        border-left: solid #00AA00;
        padding-left: 2;
    }
    .assistant {
        color: #FFFFFF;
        background: #2a2a42;
        border-left: solid #8888FF;
        padding-left: 2;
    }
    .sender {
        color: #AAAAAA;
        text-style: bold;
        margin-bottom: 1;
    }
    .content {
        margin-left: 1;
    }
    """

    def __init__(self, message: str, role: str, **kwargs: Any) -> None:
        """メッセージウィジェットを初期化する。

        Args:
            message: 表示するメッセージ
            role: メッセージの送信者（user または assistant）
            **kwargs: その他の引数

        """
        # 送信者ラベルを作成
        sender_label = "あなた" if role == "user" else "ずんだもん"
        content = f"[b]{sender_label}[/b]\n{message}"

        super().__init__(content, **kwargs)
        self.add_class(role)


class MagiSystemMessage(Static):
    """MAGIシステムの応答を表示するウィジェット."""

    DEFAULT_CSS = """
    MagiSystemMessage {
        width: 100%;
        padding: 1 1;
        margin: 1 0;
        border: solid #333333;
        border-top: none;
        border-right: none;
        border-bottom: solid #333333;
        border-left: none;
        color: #FFFFFF;
        background: #2a2a42;
        border-left: solid #8888FF;
        padding-left: 2;
    }
    .melchior {
        color: #FFD700;  /* 金色 */
        background: #2a2038;
        border-left: solid #AA0000;
    }
    .balthasar {
        color: #98FB98;  /* 薄緑色 */
        background: #1a3a2a;
        border-left: solid #00AA00;
    }
    .casper {
        color: #ADD8E6;  /* 水色 */
        background: #1a2a3a;
        border-left: solid #0000AA;
    }
    .consensus {
        color: #FFFFFF;
        background: #2a2a42;
        border-left: solid #8888FF;
    }
    .waiting {
        color: #888888;
        text-style: italic;
    }
    .header {
        color: #AAAAAA;
        text-style: bold;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        """MAGIシステムのメッセージウィジェットを初期化する."""
        super().__init__("", **kwargs)
        self.add_class("assistant")

        # 各システムの状態を初期化
        self.melchior_response = "応答待ち..."
        self.balthasar_response = "応答待ち..."
        self.casper_response = "応答待ち..."
        self.consensus_response = ""

        # 初期表示を設定
        self._update_content()

    def update_response(self, system: str, response: str) -> None:
        """指定したシステムの応答を更新する.

        Args:
            system: システム名 (melchior, balthasar, casper, consensus)
            response: 新しい応答内容

        """
        # 応答内容のマークアップ文字をエスケープする
        escaped_response = escape_markup(response)

        if system == "melchior":
            self.melchior_response = escaped_response
        elif system == "balthasar":
            self.balthasar_response = escaped_response
        elif system == "casper":
            self.casper_response = escaped_response
        elif system == "consensus":
            self.consensus_response = escaped_response

        self._update_content()

    def _update_content(self) -> None:
        """表示内容を更新する."""
        content = "[b]ずんだもん[/b]\n"
        content += "【MAGI合議システム】\n\n"

        # MELCHIOR
        melchior_class = "" if self.melchior_response != "応答待ち..." else " waiting"
        content += f"[b class='header melchior{melchior_class}']■ MELCHIOR（科学者）:[/b]\n"
        content += f"[span class='melchior{melchior_class}']{self.melchior_response}[/span]\n\n"

        # BALTHASAR
        balthasar_class = "" if self.balthasar_response != "応答待ち..." else " waiting"
        content += f"[b class='header balthasar{balthasar_class}']■ BALTHASAR（母親）:[/b]\n"
        content += f"[span class='balthasar{balthasar_class}']{self.balthasar_response}[/span]\n\n"

        # CASPER
        casper_class = "" if self.casper_response != "応答待ち..." else " waiting"
        content += f"[b class='header casper{casper_class}']■ CASPER（女性）:[/b]\n"
        content += f"[span class='casper{casper_class}']{self.casper_response}[/span]\n\n"

        # 全てのシステムから回答があれば最終判断を表示
        if self.consensus_response:
            content += "[b class='header consensus']【最終判断】[/b]\n"
            content += f"{self.consensus_response}"

        self.update(content)


class SimpleMagiMessage(Static):
    """マークアップを使わないシンプルなMAGIシステムメッセージ表示ウィジェット."""

    DEFAULT_CSS = """
    SimpleMagiMessage {
        width: 100%;
        padding: 1 1;
        margin: 1 0;
        border: solid #333333;
        border-top: none;
        border-right: none;
        border-bottom: solid #333333;
        border-left: none;
        color: #FFFFFF;
        background: #2a2a42;
        border-left: solid #8888FF;
        padding-left: 2;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        """シンプルMAGIシステムのメッセージウィジェットを初期化する."""
        super().__init__("", **kwargs)
        self.add_class("assistant")

        # 各システムの状態を初期化
        self.melchior_response = "応答待ち..."
        self.balthasar_response = "応答待ち..."
        self.casper_response = "応答待ち..."
        self.consensus_response = ""

        # 初期表示を設定
        self._update_content()

    def update_response(self, system: str, response: str) -> None:
        """指定したシステムの応答を更新する.

        Args:
            system: システム名 (melchior, balthasar, casper, consensus)
            response: 新しい応答内容

        """
        if system == "melchior":
            self.melchior_response = response
        elif system == "balthasar":
            self.balthasar_response = response
        elif system == "casper":
            self.casper_response = response
        elif system == "consensus":
            self.consensus_response = response

        self._update_content()

    def _update_content(self) -> None:
        """表示内容を更新する."""
        # マークアップを使わないシンプルな表示
        content = "ずんだもん\n"
        content += "【MAGI合議システム】\n\n"

        # MELCHIOR
        content += "■ MELCHIOR（科学者）:\n"
        content += f"{self.melchior_response}\n\n"

        # BALTHASAR
        content += "■ BALTHASAR（母親）:\n"
        content += f"{self.balthasar_response}\n\n"

        # CASPER
        content += "■ CASPER（女性）:\n"
        content += f"{self.casper_response}\n\n"

        # 全てのシステムから回答があれば最終判断を表示
        if self.consensus_response:
            content += "【最終判断】\n"
            content += f"{self.consensus_response}"

        # マークアップなしでシンプルに更新
        self.update(content)


class DebatingMagiMessage(Static):
    """討論機能を持つMAGIシステムメッセージ表示ウィジェット."""

    DEFAULT_CSS = """
    DebatingMagiMessage {
        width: 100%;
        padding: 1 1;
        margin: 1 0;
        border: solid #333333;
        border-top: none;
        border-right: none;
        border-bottom: solid #333333;
        border-left: none;
        color: #FFFFFF;
        background: #2a2a42;
        border-left: solid #8888FF;
        padding-left: 2;
    }

    .melchior {
        color: #FFD700;  /* 金色 */
        background: #2a2038;
        border-left: solid #AA0000;
    }

    .balthasar {
        color: #98FB98;  /* 薄緑色 */
        background: #1a3a2a;
        border-left: solid #00AA00;
    }

    .casper {
        color: #ADD8E6;  /* 水色 */
        background: #1a2a3a;
        border-left: solid #0000AA;
    }

    .consensus {
        color: #FFFFFF;
        background: #2a2a42;
        border-left: solid #8888FF;
    }

    .waiting {
        color: #888888;
        text-style: italic;
    }

    .phase-label {
        color: #AAAAAA;
        background: #2a2a2a;
        padding: 0 1;
        margin-right: 1;
    }

    .header {
        color: #AAAAAA;
        text-style: bold;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        """討論機能付きMAGIシステムのメッセージウィジェットを初期化する."""
        super().__init__("", **kwargs)
        self.add_class("assistant")

        # 各システムの状態を初期化（フェーズごと）
        self.melchior_responses = {"initial": "応答待ち...", "debate_1": "", "final": ""}
        self.balthasar_responses = {"initial": "応答待ち...", "debate_1": "", "final": ""}
        self.casper_responses = {"initial": "応答待ち...", "debate_1": "", "final": ""}
        self.consensus_response = ""

        # 表示するフェーズを設定
        self.current_phase = "initial"

        # 初期表示を設定
        self._update_content()

    def update_response(self, system: str, response: str, phase: str = "initial") -> None:
        """指定したシステムの応答を更新する.

        Args:
            system: システム名 (melchior, balthasar, casper, consensus)
            response: 新しい応答内容
            phase: 応答フェーズ（"initial", "debate_1", "debate_2", ..., "final"）

        """
        # 応答内容を更新
        if system == "melchior":
            self.melchior_responses[phase] = response
            # 表示フェーズを更新
            if phase != "initial":
                self.current_phase = phase
        elif system == "balthasar":
            self.balthasar_responses[phase] = response
        elif system == "casper":
            self.casper_responses[phase] = response
        elif system == "consensus":
            self.consensus_response = response
            self.current_phase = "final"

        self._update_content()

    def _update_content(self) -> None:
        """表示内容を更新する."""
        content = "ずんだもん\n"
        content += "【MAGI合議システム】\n\n"

        # 現在のフェーズに応じた表示内容を生成
        if self.current_phase == "initial":
            content += "【第一段階: 初期分析】\n\n"

            # MELCHIOR
            content += "■ MELCHIOR（科学者）:\n"
            content += f"{self.melchior_responses['initial']}\n\n"

            # BALTHASAR
            content += "■ BALTHASAR（母親）:\n"
            content += f"{self.balthasar_responses['initial']}\n\n"

            # CASPER
            content += "■ CASPER（女性）:\n"
            content += f"{self.casper_responses['initial']}\n\n"

        elif self.current_phase.startswith("debate_"):
            round_num = self.current_phase.split("_")[1]
            content += f"【第二段階: 討論 (ラウンド {round_num})】\n\n"

            # MELCHIOR
            content += "■ MELCHIOR（科学者）:\n"
            content += f"{self.melchior_responses[self.current_phase]}\n\n"

            # BALTHASAR
            content += "■ BALTHASAR（母親）:\n"
            content += f"{self.balthasar_responses[self.current_phase]}\n\n"

            # CASPER
            content += "■ CASPER（女性）:\n"
            content += f"{self.casper_responses[self.current_phase]}\n\n"

        elif self.current_phase == "final":
            content += "【第三段階: 最終判断】\n\n"

            # MELCHIOR の最終見解
            last_debate_phase = max([phase for phase in self.melchior_responses.keys() if phase.startswith("debate_")], default="initial")
            content += "■ MELCHIOR（科学者）の最終見解:\n"
            content += f"{self.melchior_responses[last_debate_phase]}\n\n"

            # BALTHASAR の最終見解
            content += "■ BALTHASAR（母親）の最終見解:\n"
            content += f"{self.balthasar_responses[last_debate_phase]}\n\n"

            # CASPER の最終見解
            content += "■ CASPER（女性）の最終見解:\n"
            content += f"{self.casper_responses[last_debate_phase]}\n\n"

            # 最終判断
            content += "【最終判断】\n"
            content += f"{self.consensus_response}"

        # マークアップなしで更新
        self.update(content)


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

    def __init__(self, provider: str = "ollama", api_base: str = None, model: str = None, **kwargs: Any) -> None:
        """チャットエリアを初期化.

        Args:
            provider: 使用するプロバイダー ("ollama" または "litellm")
            api_base: APIサーバーのベースURL (Noneの場合はデフォルト値を使用)
            model: 使用するモデル名 (Noneの場合はデフォルト値を使用)
            **kwargs: その他の引数

        """
        super().__init__(**kwargs)

        # プロバイダーに応じたデフォルト値を設定するのだ
        if api_base is None:
            if provider == "litellm":
                api_base = "http://localhost:4000"
            else:  # ollama
                api_base = "http://localhost:11434/api"

        if model is None:
            model = "phi4-mini"

        self.chat_model = ChatModel(
            api_base=api_base,
            model=model,
            api_type=provider,
        )

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

    async def get_ai_response_streaming(self, user_message: str) -> None:
        """AIからの応答をストリーミングで取得して表示.

        Args:
            user_message: ユーザーが入力したメッセージ

        """
        # MAGIシステムメッセージを作成
        message_area = self.query_one("#message-area")
        magi_message = SimpleMagiMessage()
        message_area.mount(magi_message)
        message_area.scroll_end()

        # 各MAGIシステムからの応答をストリーミングで処理
        async def update_magi_response(system, response):
            """各MAGIシステムの応答を受け取るコールバック関数"""
            magi_message.update_response(system, response)
            message_area.scroll_end()

        # ストリーミングレスポンスを取得
        async for response in self.chat_model.get_response_streaming(self.messages, update_magi_response):
            # すでにコールバックで処理されているので、ここでは何もしない
            pass

    async def get_ai_response_with_debate(self, user_message: str) -> None:
        """AIからの応答をストリーミングで取得し、討論を行った上で表示する.

        Args:
            user_message: ユーザーが入力したメッセージ

        """
        # 討論機能付きのMAGIシステムメッセージを作成
        message_area = self.query_one("#message-area")
        magi_message = DebatingMagiMessage()
        message_area.mount(magi_message)
        message_area.scroll_end()

        # 各MAGIシステムからの応答をストリーミングで処理するコールバック
        async def update_magi_response(system, response, phase):
            """各MAGIシステムの応答を受け取るコールバック関数"""
            magi_message.update_response(system, response, phase)
            message_area.scroll_end()

        # 討論を含むストリーミングレスポンスを取得 (1ラウンドの討論)
        async for response in self.chat_model.get_response_with_debate(self.messages, update_magi_response, debate_rounds=1):
            # すでにコールバックで処理されているので、ここでは何もしない
            pass

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

        # 討論機能を使ったLLMからの応答をストリーミングで取得するのだ
        await self.get_ai_response_with_debate(message)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """入力が送信されたときの処理.

        Args:
            event: 入力送信イベント

        """
        if event.input.id == "message-input":
            self.run_worker(self.send_message())


class ChatApp(App):
    """チャットアプリケーションのメインクラス."""

    TITLE = "ずんだもんとチャット"
    CSS = """
    Screen {
        background: #121212;
    }
    """

    def __init__(self, provider: str = "ollama", api_base: str = None, model: str = None):
        """チャットアプリケーションを初期化.

        Args:
            provider: 使用するプロバイダー ("ollama" または "litellm")
            api_base: APIサーバーのベースURL (Noneの場合はデフォルト値を使用)
            model: 使用するモデル名 (Noneの場合はデフォルト値を使用)

        """
        super().__init__()
        self.provider = provider
        self.api_base = api_base
        self.model = model

    def compose(self) -> ComposeResult:
        """UIコンポーネントを構成.

        Returns:
            ComposeResult: コンポーネントの構成結果

        """
        yield Header()
        yield ChatArea(provider=self.provider, api_base=self.api_base, model=self.model)
        yield Footer()
