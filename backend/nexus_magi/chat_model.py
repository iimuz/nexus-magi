"""LLMとの対話を管理するモジュール."""

from nexus_magi.debate_chat_model import DebateChatModel
from nexus_magi.simple_chat_model import SimpleChatModel


class ChatModel:
    """チャットモデルのファクトリークラス.

    適切なチャットモデルのインスタンスを作成し、既存のコードとの互換性を保ちます。
    """

    def __init__(
        self,
        api_base: str = "http://localhost:11434/api",
        model: str = "phi4-mini",
        api_type: str = "ollama",
    ) -> None:
        """チャットモデルを初期化.

        Args:
            api_base: APIサーバーのベースURL
            model: 使用するモデル名
            api_type: APIの種類("ollama" または "litellm")

        """
        self.api_base = api_base
        self.model = model
        self.api_type = api_type

        # デフォルトはシンプルなチャットモデル
        self.simple_chat_model = SimpleChatModel(api_base, model, api_type)
        self.debate_chat_model = DebateChatModel(api_base, model, api_type)

    async def get_response(self, messages: list[dict[str, str]]) -> str:
        """会話履歴を元に次の応答を生成する.

        Args:
            messages: これまでの会話履歴

        Returns:
            str: LLMからの応答

        """
        return await self.simple_chat_model.get_response(messages)

    async def get_response_streaming(
        self,
        messages: list[dict[str, str]],
        callback = None,
    ):
        """会話履歴を元に次の応答を生成し、結果をストリーミングで返す.

        Args:
            messages: これまでの会話履歴
            callback: 各MAGIシステムの応答を受け取るコールバック関数

        Yields:
            dict: MAGIシステムの応答状態の更新

        """
        async for response in self.simple_chat_model.get_response_streaming(messages, callback):
            yield response

    async def get_response_with_debate(
        self,
        messages: list[dict[str, str]],
        callback = None,
        debate_rounds: int = 1,
    ):
        """会話履歴を元に次の応答を生成し、MAGIシステム間で討論を行った上で結果を返す.

        Args:
            messages: これまでの会話履歴
            callback: 各MAGIシステムの応答を受け取るコールバック関数
            debate_rounds: 討論のラウンド数(デフォルト: 1)

        Yields:
            dict: MAGIシステムの応答状態の更新

        """
        async for response in self.debate_chat_model.get_response_with_debate(
            messages, callback, debate_rounds
        ):
            yield response
