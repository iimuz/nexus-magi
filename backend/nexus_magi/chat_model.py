"""LLMとの対話を管理するモジュール."""

import asyncio
import json
from collections.abc import AsyncGenerator, Callable
from enum import Enum
from typing import Any

import requests
from langgraph.graph import END, StateGraph

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
            api_type: APIの種類("ollama" または "litellm")

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
            melchior_response: str | None = None
            balthasar_response: str | None = None
            casper_response: str | None = None
            final_response: str | None = None

        # 各MAGIシステムのノードを定義するのだ
        def generate_melchior_response(state: State) -> State:
            """MELCHIOR: 科学者のように論理的・分析的に考えるシステム."""
            messages = self._add_system_instructions(
                state["messages"], MagiSystem.MELCHIOR
            )

            if self.api_type == "ollama":
                response = self._call_ollama_api(messages)
            else:  # litellm
                response = self._call_litellm_api(messages)

            state["melchior_response"] = response
            return state

        def generate_balthasar_response(state: State) -> State:
            """BALTHASAR: 母親のように共感的・感情的に考えるシステム."""
            messages = self._add_system_instructions(
                state["messages"], MagiSystem.BALTHASAR
            )

            if self.api_type == "ollama":
                response = self._call_ollama_api(messages)
            else:  # litellm
                response = self._call_litellm_api(messages)

            state["balthasar_response"] = response
            return state

        def generate_casper_response(state: State) -> State:
            """CASPER: 女性のように直感的・創造的に考えるシステム."""
            messages = self._add_system_instructions(
                state["messages"], MagiSystem.CASPER
            )

            if self.api_type == "ollama":
                response = self._call_ollama_api(messages)
            else:  # litellm
                response = self._call_litellm_api(messages)

            state["casper_response"] = response
            return state

        def consensus_vote(state: State) -> State:
            """3つのMAGIシステムの応答を合議して最終結果を導き出す."""
            melchior = state.get(
                "melchior_response", "レスポンスが取得できませんでした"
            )
            balthasar = state.get(
                "balthasar_response", "レスポンスが取得できませんでした"
            )
            casper = state.get("casper_response", "レスポンスが取得できませんでした")

            # 合議結果を作成する
            final_response = (
                f"【MAGI合議システム - 判定結果】\n\n"
                f"■ MELCHIOR(科学者)の見解:\n{melchior}\n\n"
                f"■ BALTHASAR(母親)の見解:\n{balthasar}\n\n"
                f"■ CASPER(女性)の見解:\n{casper}\n\n"
                f"【最終判断】\n"
                f"以上の3つの視点を総合して判断するのだ。\n"
            )

            state["final_response"] = final_response
            return state

        # グラフを作成するのだ
        graph = StateGraph(State)

        # ノードを追加
        graph.add_node("melchior", generate_melchior_response)
        graph.add_node("balthasar", generate_balthasar_response)
        graph.add_node("casper", generate_casper_response)
        graph.add_node("consensus", consensus_vote)

        # シンプルなシーケンシャルパターンでグラフを構築
        # 開始点から各MAGIシステムを実行し、最後にコンセンサスで合議する
        graph.add_edge("melchior", "balthasar")
        graph.add_edge("balthasar", "casper")
        graph.add_edge("casper", "consensus")
        graph.add_edge("consensus", END)

        # グラフの開始点を設定
        graph.set_entry_point("melchior")

        return graph.compile()

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
            None, lambda: self.graph.invoke({"messages": messages})
        )

        return result["final_response"]

    async def get_response_streaming(
        self,
        messages: list[dict[str, str]],
        callback: Callable[[str, str], None] | None = None,
    ) -> AsyncGenerator[dict[str, str], None]:
        """会話履歴を元に次の応答を生成し、結果をストリーミングで返す.

        Args:
            messages: これまでの会話履歴
            callback: 各MAGIシステムの応答を受け取るコールバック関数

        Yields:
            dict: MAGIシステムの応答状態の更新

        """
        # MAGIシステムの応答を順次処理する
        state = {"messages": messages}

        # MELCHIOR
        state = await self._get_magi_response(state, MagiSystem.MELCHIOR)
        melchior_response = state.get(
            "melchior_response", "レスポンスが取得できませんでした"
        )
        if callback:
            await callback("melchior", melchior_response)
        yield {"system": "melchior", "response": melchior_response}

        # BALTHASAR
        state = await self._get_magi_response(state, MagiSystem.BALTHASAR)
        balthasar_response = state.get(
            "balthasar_response", "レスポンスが取得できませんでした"
        )
        if callback:
            await callback("balthasar", balthasar_response)
        yield {"system": "balthasar", "response": balthasar_response}

        # CASPER
        state = await self._get_magi_response(state, MagiSystem.CASPER)
        casper_response = state.get(
            "casper_response", "レスポンスが取得できませんでした"
        )
        if callback:
            await callback("casper", casper_response)
        yield {"system": "casper", "response": casper_response}

        # 最終的な合議結果を生成
        final_response = (
            f"【MAGI合議システム - 判定結果】\n\n"
            f"■ MELCHIOR(科学者)の見解:\n{melchior_response}\n\n"
            f"■ BALTHASAR(母親)の見解:\n{balthasar_response}\n\n"
            f"■ CASPER(女性)の見解:\n{casper_response}\n\n"
            f"【最終判断】\n"
            f"以上の3つの視点を総合して判断するのだ。\n"
        )

        if callback:
            await callback("consensus", final_response)
        yield {"system": "consensus", "response": final_response}

    async def _get_magi_response(
        self, state: dict[str, Any], magi_type: MagiSystem
    ) -> dict[str, Any]:
        """指定したMAGIシステムの応答を非同期で取得する.

        Args:
            state: 現在の状態
            magi_type: MAGIシステムの種類

        Returns:
            dict: 更新された状態

        """
        messages = self._add_system_instructions(state["messages"], magi_type)

        loop = asyncio.get_event_loop()
        if self.api_type == "ollama":
            response = await loop.run_in_executor(
                None, lambda: self._call_ollama_api(messages)
            )
        else:  # litellm
            response = await loop.run_in_executor(
                None, lambda: self._call_litellm_api(messages)
            )

        # MAGIシステムに応じた応答を状態に追加
        if magi_type == MagiSystem.MELCHIOR:
            state["melchior_response"] = response
        elif magi_type == MagiSystem.BALTHASAR:
            state["balthasar_response"] = response
        elif magi_type == MagiSystem.CASPER:
            state["casper_response"] = response

        return state

    async def get_response_with_debate(
        self,
        messages: list[dict[str, str]],
        callback: Callable[[str, str, str], None] | None = None,
        debate_rounds: int = 1,
    ) -> AsyncGenerator[dict[str, str], None]:
        """会話履歴を元に次の応答を生成し、MAGIシステム間で討論を行った上で結果を返す.

        Args:
            messages: これまでの会話履歴
            callback: 各MAGIシステムの応答を受け取るコールバック関数
            debate_rounds: 討論のラウンド数(デフォルト: 1)

        Yields:
            dict: MAGIシステムの応答状態の更新

        """
        # 初期の状態
        state = {"messages": messages}

        # 各MAGIシステムの初期応答を取得
        # MELCHIOR(科学者)の初期応答
        state = await self._get_magi_response(state, MagiSystem.MELCHIOR)
        melchior_response = state.get(
            "melchior_response", "レスポンスが取得できませんでした"
        )
        if callback:
            await callback("melchior", melchior_response, "initial")
        yield {"system": "melchior", "response": melchior_response, "phase": "initial"}

        # BALTHASAR(母親)の初期応答
        state = await self._get_magi_response(state, MagiSystem.BALTHASAR)
        balthasar_response = state.get(
            "balthasar_response", "レスポンスが取得できませんでした"
        )
        if callback:
            await callback("balthasar", balthasar_response, "initial")
        yield {
            "system": "balthasar",
            "response": balthasar_response,
            "phase": "initial",
        }

        # CASPER(女性)の初期応答
        state = await self._get_magi_response(state, MagiSystem.CASPER)
        casper_response = state.get(
            "casper_response", "レスポンスが取得できませんでした"
        )
        if callback:
            await callback("casper", casper_response, "initial")
        yield {"system": "casper", "response": casper_response, "phase": "initial"}

        # 討論ラウンド
        melchior_final = melchior_response
        balthasar_final = balthasar_response
        casper_final = casper_response

        for round_num in range(debate_rounds):
            # 討論用のプロンプトを作成
            debate_prompt = f"""
これまでの議論を踏まえて、あなたの立場から意見を改めて述べてください。
他のMAGIシステムの意見に対して同意または反論し、自分の視点から分析してください。

【質問】
{messages[-1]["content"]}

【MELCHIOR(科学者)の見解】
{melchior_final}

【BALTHASAR(母親)の見解】
{balthasar_final}

【CASPER(女性)の見解】
{casper_final}

あなたの立場からの分析と結論を述べてください。
"""

            # MELCHIORの討論
            melchior_debate_messages = [
                {
                    "role": "system",
                    "content": (
                        f"あなたはMAGIシステムの{MagiSystem.MELCHIOR.value}です。"
                        f"{MagiPersonality.MELCHIOR.value}として回答してください。"
                    ),
                },
                {"role": "user", "content": debate_prompt},
            ]

            # キャプチャした変数を使用するために別の関数を定義
            def _call_melchior_api(
                api_type: str, messages_local: list[dict[str, Any]]
            ) -> str:
                if api_type == "ollama":
                    return self._call_ollama_api(messages_local)
                return self._call_litellm_api(messages_local)

            # ラムダ内で明示的に変数を渡して、適切にバインドします
            melchior_debate_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda messages=melchior_debate_messages: _call_melchior_api(
                    self.api_type, messages
                ),
            )

            melchior_final = melchior_debate_response
            if callback:
                await callback(
                    "melchior", melchior_debate_response, f"debate_{round_num + 1}"
                )
            yield {
                "system": "melchior",
                "response": melchior_debate_response,
                "phase": f"debate_{round_num + 1}",
            }

            # BALTHASARの討論
            balthasar_debate_messages = [
                {
                    "role": "system",
                    "content": (
                        f"あなたはMAGIシステムの{MagiSystem.BALTHASAR.value}です。"
                        f"{MagiPersonality.BALTHASAR.value}として回答してください。"
                    ),
                },
                {"role": "user", "content": debate_prompt},
            ]

            # キャプチャした変数を使用するために別の関数を定義
            def _call_balthasar_api(
                api_type: str, messages_local: list[dict[str, Any]]
            ) -> str:
                if api_type == "ollama":
                    return self._call_ollama_api(messages_local)
                return self._call_litellm_api(messages_local)

            # ラムダ内で明示的に変数を渡して、適切にバインドします
            balthasar_debate_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda messages=balthasar_debate_messages: _call_balthasar_api(
                    self.api_type, messages
                ),
            )

            balthasar_final = balthasar_debate_response
            if callback:
                await callback(
                    "balthasar", balthasar_debate_response, f"debate_{round_num + 1}"
                )
            yield {
                "system": "balthasar",
                "response": balthasar_debate_response,
                "phase": f"debate_{round_num + 1}",
            }

            # CASPERの討論
            casper_debate_messages = [
                {
                    "role": "system",
                    "content": (
                        f"あなたはMAGIシステムの{MagiSystem.CASPER.value}です。"
                        f"{MagiPersonality.CASPER.value}として回答してください。"
                    ),
                },
                {"role": "user", "content": debate_prompt},
            ]

            # キャプチャした変数を使用するために別の関数を定義
            def _call_casper_api(
                api_type: str, messages_local: list[dict[str, Any]]
            ) -> str:
                if api_type == "ollama":
                    return self._call_ollama_api(messages_local)
                return self._call_litellm_api(messages_local)

            # ラムダ内で明示的に変数を渡して、適切にバインドします
            casper_debate_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda messages=casper_debate_messages: _call_casper_api(
                    self.api_type, messages
                ),
            )

            casper_final = casper_debate_response
            if callback:
                await callback(
                    "casper", casper_debate_response, f"debate_{round_num + 1}"
                )
            yield {
                "system": "casper",
                "response": casper_debate_response,
                "phase": f"debate_{round_num + 1}",
            }

        # 最終的な合議結果を生成
        consensus_prompt = f"""
以下のMAGIシステム3つの分析結果に基づいて、最終的な判断を下してください。
各システムの視点を統合し、バランスの取れた結論を導き出してください。

【質問】
{messages[-1]["content"]}

【MELCHIOR(科学者)の最終見解】
{melchior_final}

【BALTHASAR(母親)の最終見解】
{balthasar_final}

【CASPER(女性)の最終見解】
{casper_final}

3つの視点を総合した最終判断を述べてください。
"""

        consensus_messages = [
            {
                "role": "system",
                "content": "あなたはMAGI合議システムです。3つのMAGIシステムの判断を"
                "総合して最終的な結論を出してください。",
            },
            {"role": "user", "content": consensus_prompt},
        ]

        # キャプチャした変数を使用するために別の関数を定義
        def _call_consensus_api(api_type: str, messages: list[dict[str, Any]]) -> str:
            if api_type == "ollama":
                return self._call_ollama_api(messages)
            return self._call_litellm_api(messages)

        consensus_response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda messages=consensus_messages: _call_consensus_api(
                self.api_type, messages
            ),
        )

        # 最終的な合議結果
        final_response = (
            f"【MAGI合議システム - 討論結果】\n\n"
            f"■ MELCHIOR(科学者)の最終見解:\n{melchior_final}\n\n"
            f"■ BALTHASAR(母親)の最終見解:\n{balthasar_final}\n\n"
            f"■ CASPER(女性)の最終見解:\n{casper_final}\n\n"
            f"【最終判断】\n{consensus_response}\n"
        )

        if callback:
            await callback("consensus", final_response, "final")
        yield {"system": "consensus", "response": final_response, "phase": "final"}
