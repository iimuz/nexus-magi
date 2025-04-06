"""LLMとの対話を管理するモジュール."""

import asyncio
import json
from typing import Any

import requests
from langgraph.graph import END, StateGraph


class ChatModel:
    """チャットモデルを管理するクラス."""

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
            api_type: APIの種類（"ollama" または "litellm"）

        """
        self.api_base = api_base
        self.model = model
        self.api_type = api_type
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        """langgraphのグラフを作成.

        Returns:
            StateGraph: 作成されたグラフ

        """
        # グラフの状態の型を定義するのだ
        class State(dict[str, Any]):
            """グラフの状態を表す型."""

            messages: list[dict[str, str]]
            response: str | None = None

        # グラフのノードを定義するのだ
        def generate_response(state: State) -> State:
            """LLMを使って応答を生成.

            Args:
                state: 現在の状態

            Returns:
                State: 更新された状態

            """
            messages = state["messages"]

            if self.api_type == "ollama":
                response = self._call_ollama_api(messages)
            else:  # litellm
                response = self._call_litellm_api(messages)

            # 応答を状態に追加するのだ
            state["response"] = response
            return state

        # グラフを作成するのだ
        graph = StateGraph(State)
        graph.add_node("generate_response", generate_response)

        # エッジを定義するのだ
        graph.set_entry_point("generate_response")
        graph.add_edge("generate_response", END)

        return graph.compile()

    def _call_ollama_api(self, messages: list[dict[str, str]]) -> str:
        """OllamaのAPIを呼び出して応答を取得する.

        Args:
            messages: これまでの会話履歴

        Returns:
            str: LLMからの応答

        """
        # Ollamaの場合、会話履歴を整形するのだ
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

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

        if response.status_code != 200:
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
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

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

        if response.status_code != 200:
            return f"エラーが発生したのだ: {response.status_code} - {response.text}"

        try:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except (KeyError, json.JSONDecodeError) as e:
            return f"応答の解析に失敗したのだ: {e!s}"

    async def get_response(self, messages: list[dict[str, str]]) -> str:
        """会話履歴を元に次の応答を生成する.

        Args:
            messages: これまでの会話履歴

        Returns:
            str: LLMからの応答

        """
        # 非同期で実行するために、ThreadPoolExecutorを使うのだ
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.graph.invoke({"messages": messages})
        )

        return result["response"]
