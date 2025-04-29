"""LLMとの対話を管理する基底モジュール."""

import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

import requests

# HTTPステータスコード
HTTP_OK = 200


class MagiSystem(Enum):
    """MAGIシステムの種類を表す列挙型."""

    MELCHIOR = "melchior"
    BALTHASAR = "balthasar"
    CASPER = "casper"


class MagiPersonality(Enum):
    """MAGIシステムの個性を表す列挙型."""

    MELCHIOR = "科学者: 論理的・分析的に考えるシステム"
    BALTHASAR = "母親: 共感的・感情的に考えるシステム"
    CASPER = "女性: 直感的・創造的に考えるシステム"


class BaseChatModel(ABC):
    """チャットモデルを管理する基底クラス."""

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

    def _add_system_instructions(
        self, messages: list[dict[str, str]], magi_type: MagiSystem
    ) -> list[dict[str, str]]:
        """各MAGIシステムの特性に合わせたシステムプロンプトを追加する.

        Args:
            messages: 元のメッセージリスト
            magi_type: MAGIシステムの種類

        Returns:
            list[dict[str, str]]: システムプロンプトを追加したメッセージリスト

        """
        # メッセージのコピーを作成
        new_messages = messages.copy()

        # システム指示を作成
        personality = MagiPersonality[magi_type.name].value

        # システムメッセージがあれば更新、なければ追加
        system_msg_found = False
        for i, msg in enumerate(new_messages):
            if msg["role"] == "system":
                new_messages[i] = {
                    "role": "system",
                    "content": (
                        f"あなたはMAGIシステムの{magi_type.value}です。"
                        f"{personality}として回答してください。"
                    ),
                }
                system_msg_found = True
                break

        if not system_msg_found:
            # 先頭にシステムメッセージを追加
            new_messages.insert(
                0,
                {
                    "role": "system",
                    "content": (
                        f"あなたはMAGIシステムの{magi_type.value}です。"
                        f"{personality}として回答してください。"
                    ),
                },
            )

        return new_messages

    def _call_ollama_api(self, messages: list[dict[str, str]]) -> str:
        """OllamaのAPIを呼び出して応答を取得する.

        Args:
            messages: これまでの会話履歴

        Returns:
            str: LLMからの応答

        """
        # Ollamaの場合、会話履歴を整形するのだ
        formatted_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in messages
        ]

        # APIリクエストを送信するのだ
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
            return f"エラーが発生したのだ: {response.status_code} - {response.text}"

        try:
            result = response.json()
            # Ollamaの応答形式に合わせてパースするのだ
            # Ollamaの応答は {"message": {"content": "応答テキスト"}} 形式なのだ
            return result["message"]["content"]
        except (KeyError, json.JSONDecodeError) as e:
            return f"応答の解析に失敗したのだ: {e!s}"

    def _call_litellm_api(self, messages: list[dict[str, str]]) -> str:
        """LiteLLMのAPIを呼び出して応答を取得する.

        Args:
            messages: これまでの会話履歴

        Returns:
            str: LLMからの応答

        """
        # LiteLLMの場合、会話履歴を整形するのだ
        formatted_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in messages
        ]

        # APIリクエストを送信するのだ
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
            return f"エラーが発生したのだ: {response.status_code} - {response.text}"

        try:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except (KeyError, json.JSONDecodeError) as e:
            return f"応答の解析に失敗したのだ: {e!s}"

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

    @abstractmethod
    async def get_response(self, messages: list[dict[str, str]]) -> str:
        """会話履歴を元に次の応答を生成する.

        Args:
            messages: これまでの会話履歴

        Returns:
            str: LLMからの応答

        """
