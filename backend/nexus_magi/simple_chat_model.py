"""シンプルな対話を管理するモジュール."""

import asyncio
import json
from collections.abc import AsyncGenerator, Callable
from typing import Any

import requests

# HTTPステータスコード
HTTP_OK = 200


class SimpleChatModel:
    """シンプルなチャットモデルを管理するクラス."""

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

    def _call_ollama_api(self, messages: list[dict[str, str]]) -> str:
        """OllamaのAPIを呼び出して応答を取得する.

        Args:
            messages: これまでの会話履歴

        Returns:
            str: LLMからの応答

        """
        # Ollamaの場合、会話履歴を整形する
        formatted_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in messages
        ]

        # APIリクエストを送信する
        response = requests.post(
            f"{self.api_base}/chat",
            json={
                "model": self.model,
                "messages": formatted_messages,
                "stream": False,
            },
            timeout=60,
        )

        if response.status_code != HTTP_OK:
            return f"エラーが発生しました: {response.status_code} - {response.text}"

        try:
            result = response.json()
            # Ollamaの応答形式に合わせてパースする
            # Ollamaの応答は {"message": {"content": "応答テキスト"}} 形式
            return result["message"]["content"]
        except (KeyError, json.JSONDecodeError) as e:
            return f"応答の解析に失敗しました: {e!s}"

    def _call_litellm_api(self, messages: list[dict[str, str]]) -> str:
        """LiteLLMのAPIを呼び出して応答を取得する.

        Args:
            messages: これまでの会話履歴

        Returns:
            str: LLMからの応答

        """
        # LiteLLMの場合、会話履歴を整形する
        formatted_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in messages
        ]

        # APIリクエストを送信する
        response = requests.post(
            f"{self.api_base}/chat/completions",
            json={
                "model": self.model,
                "messages": formatted_messages,
                "stream": False,
            },
            timeout=60,
        )

        if response.status_code != HTTP_OK:
            return f"エラーが発生しました: {response.status_code} - {response.text}"

        try:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except (KeyError, json.JSONDecodeError) as e:
            return f"応答の解析に失敗しました: {e!s}"

    def _call_api(self, messages: list[dict[str, Any]]) -> str:
        """APIタイプに応じて適切なAPI呼び出しを行う.

        Args:
            messages: メッセージリスト

        Returns:
            str: API呼び出しの結果

        """
        if self.api_type == "ollama":
            return self._call_ollama_api(messages)
        return self._call_litellm_api(messages)

    async def get_response(self, messages: list[dict[str, str]]) -> str:
        """会話履歴を元に次の応答を生成する.

        Args:
            messages: これまでの会話履歴

        Returns:
            str: LLMからの単一の応答

        """
        # 非同期で実行するために、ThreadPoolExecutorを使用
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._call_api(messages))

    async def get_response_streaming(
        self,
        messages: list[dict[str, str]],
        callback: Callable[[str, str], None] | None = None,
    ) -> AsyncGenerator[dict[str, str], None]:
        """会話履歴を元に次の応答を生成し、結果をストリーミングで返す.

        Args:
            messages: これまでの会話履歴
            callback: 応答を受け取るコールバック関数

        Yields:
            dict: チャットモデルの応答状態の更新

        """
        # 単一の応答を取得
        response = await self.get_response(messages)

        # コールバックを実行
        if callback:
            await callback("melchior", response)

        # 結果をyield - melchiorシステムとして応答すると、
        # 既存のフロントエンドコードと互換性がある
        yield {"system": "melchior", "response": response, "phase": "initial"}
