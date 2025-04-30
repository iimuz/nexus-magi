"""チャットAPIサーバーを定義するモジュール."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from nexus_magi.debate_chat_model import DebateChatModel
from nexus_magi.simple_chat_model import SimpleChatModel


class APIConfig:
    """APIの設定を管理するクラス."""

    def __init__(
        self,
        api_base: str = "http://localhost:11434/api",
        model: str = "phi4-mini",
        api_type: str = "ollama",
    ) -> None:
        """APIConfigクラスを初期化.

        Args:
            api_base: LLM APIのベースURL
            model: 使用するモデル名
            api_type: APIの種類("ollama"または"litellm")

        """
        self.api_base = api_base
        self.model = model
        self.api_type = api_type


# APIの設定
api_config = APIConfig()


class ChatMessage(BaseModel):
    """チャットメッセージのモデル."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """チャットリクエストのモデル."""

    messages: list[ChatMessage]
    stream: bool = False
    debate: bool = False
    debate_rounds: int = 1


class ChatResponse(BaseModel):
    """チャットレスポンスのモデル."""

    response: str


class ConnectionManager:
    """WebSocket接続を管理するクラス."""

    def __init__(self) -> None:
        """WebSocket接続管理クラスを初期化."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """WebSocket接続を確立."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """WebSocket接続を切断."""
        self.active_connections.remove(websocket)


app = FastAPI(
    title="Nexus MAGI API",
    description="MAGIシステムによるチャットAPI",
    version="0.1.0",
)

# CORS設定を追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンに制限すべきです
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket接続マネージャー
manager = ConnectionManager()


def format_messages(messages: list[ChatMessage]) -> list[dict[str, str]]:
    """Pydanticモデルのメッセージリストを辞書リストに変換."""
    return [{"role": msg.role, "content": msg.content} for msg in messages]


@app.get("/")
async def root() -> dict[str, str]:
    """ルートエンドポイント."""
    return {"message": "MAGI合議システム API"}


@app.websocket("/api/chat/ws")
async def chat_websocket_endpoint(websocket: WebSocket) -> None:
    """通常チャット用WebSocketエンドポイント."""
    await manager.connect(websocket)
    try:
        while True:
            # クライアントからのメッセージを待機
            data = await websocket.receive_json()

            # ChatRequestの形式に変換
            request = ChatRequest(**data)
            messages = format_messages(request.messages)

            # グローバル設定を使用
            api_base = api_config.api_base
            model = api_config.model
            api_type = api_config.api_type

            # SimpleChatModelを使用
            chat_model = SimpleChatModel(api_base=api_base, model=model, api_type=api_type)

            if request.stream:
                # ストリーミングモードの場合

                # コールバック関数を定義
                async def send_update(system: str, response: str) -> None:
                    """ストリーミングモードでの更新をクライアントに送信."""
                    # phaseパラメータを追加してフロントエンドとのインターフェースを統一
                    response_data = {
                        "system": system,
                        "response": response,
                        "phase": "initial",  # 互換性のためにphaseを追加
                    }
                    await websocket.send_json(response_data)

                # ストリーミングレスポンスを生成
                async for _response in chat_model.get_response_streaming(
                    messages, send_update
                ):
                    # すでにコールバックで処理されているので、ここでは何もしない
                    pass
            else:
                # 非ストリーミングモードの場合
                response = await chat_model.get_response(messages)
                response_data = {
                    "system": "melchior",  # シンプルモードではmelchiorとして応答
                    "response": response,
                    "phase": "initial",  # 単一の応答なのでinitialフェーズとする
                }
                await websocket.send_json(response_data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/api/debate/ws")
async def debate_websocket_endpoint(websocket: WebSocket) -> None:
    """討論モード用WebSocketエンドポイント."""
    await manager.connect(websocket)
    try:
        while True:
            # クライアントからのメッセージを待機
            data = await websocket.receive_json()

            # ChatRequestの形式に変換
            request = ChatRequest(**data)
            messages = format_messages(request.messages)

            # グローバル設定を使用
            api_base = api_config.api_base
            model = api_config.model
            api_type = api_config.api_type

            # 討論モードはDebateChatModelを使用
            chat_model = DebateChatModel(api_base=api_base, model=model, api_type=api_type)

            # コールバック関数を定義
            async def send_update(system: str, response: str, phase: str) -> None:
                """討論モードでの更新をクライアントに送信."""
                response_data = {
                    "system": system,
                    "response": response,
                    "phase": phase,
                }
                await websocket.send_json(response_data)

            # 討論を含むストリーミングレスポンスを生成
            async for _response in chat_model.get_response_with_debate(
                messages, send_update, debate_rounds=request.debate_rounds
            ):
                # すでにコールバックで処理されているので、ここでは何もしない
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# アプリケーションを実行する関数
def run_app(
    host: str = "127.0.0.1",
    port: int = 8000,
    api_base: str | None = None,
    model: str | None = None,
    api_type: str | None = None,
) -> None:
    """APIサーバーを実行する.

    Args:
        host: サーバーのホスト
        port: サーバーのポート
        api_base: LLM APIのベースURL
        model: 使用するモデル名
        api_type: APIの種類("ollama"または"litellm")

    """
    import uvicorn

    # グローバル設定を更新
    if api_base is not None:
        api_config.api_base = api_base
    if model is not None:
        api_config.model = model
    if api_type is not None:
        api_config.api_type = api_type

    # サーバー起動
    uvicorn.run(app, host=host, port=port)
