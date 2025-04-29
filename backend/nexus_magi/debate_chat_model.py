"""討論モード対話を管理するモジュール."""

import asyncio
from collections.abc import AsyncGenerator, Callable
from typing import Any

from nexus_magi.base_chat_model import BaseChatModel, MagiPersonality, MagiSystem


class DebateChatModel(BaseChatModel):
    """討論モードのチャットモデルを管理するクラス."""

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
        super().__init__(api_base, model, api_type)

    async def get_response(self, messages: list[dict[str, str]]) -> str:
        """会話履歴を元に次の応答を生成する.

        Args:
            messages: これまでの会話履歴

        Returns:
            str: LLMからの応答

        """
        # 非同期ジェネレータを使用して全ての応答を取得
        final_response = None
        async for response in self.get_response_with_debate(messages, debate_rounds=1):
            if response["system"] == "consensus" and response["phase"] == "final":
                final_response = response["response"]

        # 最終的な合議結果を返す
        return final_response or "応答の生成に失敗しました"

    async def _get_magi_debate_response(
        self,
        magi_type: MagiSystem,
        magi_personality: MagiPersonality,
        debate_prompt: str,
        callback: Callable[[str, str, str], None] | None,
        phase: str,
    ) -> str:
        """特定のMAGIシステムの討論応答を取得する.

        Args:
            magi_type: MAGIシステムの種類
            magi_personality: MAGIシステムの個性
            debate_prompt: 討論用のプロンプト
            callback: コールバック関数
            phase: 現在のフェーズ

        Returns:
            str: MAGIシステムの討論応答

        """
        debate_messages = [
            {
                "role": "system",
                "content": (
                    f"あなたはMAGIシステムの{magi_type.value}です。"
                    f"{magi_personality.value}として回答してください。"
                ),
            },
            {"role": "user", "content": debate_prompt},
        ]

        # API呼び出しを実行
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._call_api(debate_messages),
        )

        # コールバックを実行
        if callback:
            await callback(magi_type.value, response, phase)

        # 結果をyieldするためのdictを返す
        return response

    def _create_debate_prompt(
        self,
        user_question: str,
        melchior_response: str,
        balthasar_response: str,
        casper_response: str,
    ) -> str:
        """討論用のプロンプトを作成する.

        Args:
            user_question: ユーザーの質問
            melchior_response: MELCHIORの応答
            balthasar_response: BALTHASARの応答
            casper_response: CASPERの応答

        Returns:
            str: 討論用のプロンプト

        """
        return f"""
これまでの議論を踏まえて、あなたの立場から意見を改めて述べてください。
他のMAGIシステムの意見に対して同意または反論し、自分の視点から分析してください。

【質問】
{user_question}

【MELCHIOR(科学者)の見解】
{melchior_response}

【BALTHASAR(母親)の見解】
{balthasar_response}

【CASPER(女性)の見解】
{casper_response}

あなたの立場からの分析と結論を述べてください。
"""

    def _create_consensus_prompt(
        self,
        user_question: str,
        melchior_final: str,
        balthasar_final: str,
        casper_final: str,
    ) -> str:
        """合議結果用のプロンプトを作成する.

        Args:
            user_question: ユーザーの質問
            melchior_final: MELCHIORの最終応答
            balthasar_final: BALTHASARの最終応答
            casper_final: CASPERの最終応答

        Returns:
            str: 合議結果用のプロンプト

        """
        return f"""
以下のMAGIシステム3つの分析結果に基づいて、最終的な判断を下してください。
各システムの視点を統合し、バランスの取れた結論を導き出してください。

【質問】
{user_question}

【MELCHIOR(科学者)の最終見解】
{melchior_final}

【BALTHASAR(母親)の最終見解】
{balthasar_final}

【CASPER(女性)の最終見解】
{casper_final}

3つの視点を総合した最終判断を述べてください。
"""

    def _create_final_response(
        self,
        melchior_final: str,
        balthasar_final: str,
        casper_final: str,
        consensus_response: str,
    ) -> str:
        """最終的な合議結果を作成する.

        Args:
            melchior_final: MELCHIORの最終応答
            balthasar_final: BALTHASARの最終応答
            casper_final: CASPERの最終応答
            consensus_response: 合議システムの応答

        Returns:
            str: 最終的な合議結果

        """
        return (
            f"【MAGI合議システム - 討論結果】\n\n"
            f"■ MELCHIOR(科学者)の最終見解:\n{melchior_final}\n\n"
            f"■ BALTHASAR(母親)の最終見解:\n{balthasar_final}\n\n"
            f"■ CASPER(女性)の最終見解:\n{casper_final}\n\n"
            f"【最終判断】\n{consensus_response}\n"
        )

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
        user_question = messages[-1]["content"]

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

        # 討論ラウンドを実行
        for round_num in range(debate_rounds):
            phase = f"debate_{round_num + 1}"

            # 討論用のプロンプトを作成
            debate_prompt = self._create_debate_prompt(
                user_question, melchior_final, balthasar_final, casper_final
            )

            # 各MAGIシステムの討論応答を取得
            melchior_debate_response = await self._get_magi_debate_response(
                MagiSystem.MELCHIOR,
                MagiPersonality.MELCHIOR,
                debate_prompt,
                callback,
                phase,
            )
            melchior_final = melchior_debate_response
            yield {
                "system": "melchior",
                "response": melchior_debate_response,
                "phase": phase,
            }

            balthasar_debate_response = await self._get_magi_debate_response(
                MagiSystem.BALTHASAR,
                MagiPersonality.BALTHASAR,
                debate_prompt,
                callback,
                phase,
            )
            balthasar_final = balthasar_debate_response
            yield {
                "system": "balthasar",
                "response": balthasar_debate_response,
                "phase": phase,
            }

            casper_debate_response = await self._get_magi_debate_response(
                MagiSystem.CASPER,
                MagiPersonality.CASPER,
                debate_prompt,
                callback,
                phase,
            )
            casper_final = casper_debate_response
            yield {
                "system": "casper",
                "response": casper_debate_response,
                "phase": phase,
            }

        # 最終的な合議結果を生成
        consensus_prompt = self._create_consensus_prompt(
            user_question, melchior_final, balthasar_final, casper_final
        )

        consensus_messages = [
            {
                "role": "system",
                "content": "あなたはMAGI合議システムです。3つのMAGIシステムの判断を"
                "総合して最終的な結論を出してください。",
            },
            {"role": "user", "content": consensus_prompt},
        ]

        consensus_response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._call_api(consensus_messages),
        )

        # 最終的な合議結果
        final_response = self._create_final_response(
            melchior_final, balthasar_final, casper_final, consensus_response
        )

        if callback:
            await callback("consensus", final_response, "final")
        yield {"system": "consensus", "response": final_response, "phase": "final"}

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
        response = await loop.run_in_executor(
            None, lambda: self._call_api(messages)
        )

        # MAGIシステムに応じた応答を状態に追加
        if magi_type == MagiSystem.MELCHIOR:
            state["melchior_response"] = response
        elif magi_type == MagiSystem.BALTHASAR:
            state["balthasar_response"] = response
        elif magi_type == MagiSystem.CASPER:
            state["casper_response"] = response

        return state
