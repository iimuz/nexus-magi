"""チャットAPIサーバーを定義するモジュール."""


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.nexus_magi.chat_model import ChatModel

# グローバル設定変数
_API_BASE = "http://localhost:11434/api"  # デフォルト値を設定
_MODEL = "phi4-mini"  # デフォルト値を設定
_API_TYPE = "ollama"

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

    def __init__(self):
        """WebSocket接続管理クラスを初期化."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """WebSocket接続を確立."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
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
async def root():
    """ルートエンドポイント."""
    return {"message": "MAGI合議システム API"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """チャットエンドポイント."""
    # グローバル設定を使用してチャットモデルをインスタンス化
    api_base = _API_BASE or "http://localhost:11434/api"  # デフォルト値を保証
    model = _MODEL or "phi4-mini"  # デフォルト値を保証

    chat_model = ChatModel(
        api_base=api_base,
        model=model,
        api_type=_API_TYPE
    )
    messages = format_messages(request.messages)

    # 通常の応答（非ストリーミング）
    response = await chat_model.get_response(messages)
    return ChatResponse(response=response)


@app.websocket("/api/chat/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocketエンドポイント."""
    await manager.connect(websocket)
    try:
        while True:
            # クライアントからのメッセージを待機
            data = await websocket.receive_json()
            print(f"WebSocketから受信したデータ: {data}")

            # ChatRequestの形式に変換
            request = ChatRequest(**data)
            messages = format_messages(request.messages)

            # グローバル設定を使用してチャットモデルをインスタンス化
            api_base = _API_BASE or "http://localhost:11434/api"  # デフォルト値を保証
            model = _MODEL or "phi4-mini"  # デフォルト値を保証

            chat_model = ChatModel(
                api_base=api_base,
                model=model,
                api_type=_API_TYPE
            )

            if request.debate:
                # 討論モードの場合
                async def send_update(system: str, response: str, phase: str):
                    """討論モードでの更新をクライアントに送信."""
                    response_data = {
                        "system": system,
                        "response": response,
                        "phase": phase
                    }
                    print(f"クライアントに送信するデータ (討論モード): {response_data}")
                    await websocket.send_json(response_data)

                # 討論を含むストリーミングレスポンスを生成
                async for response in chat_model.get_response_with_debate(
                    messages, send_update, debate_rounds=request.debate_rounds
                ):
                    # すでにコールバックで処理されているので、ここでは何もしない
                    pass

            elif request.stream:
                # 通常のストリーミングモードの場合
                async def send_update(system: str, response: str):
                    """ストリーミングモードでの更新をクライアントに送信."""
                    # phaseパラメータを追加してフロントエンドとのインターフェースを統一
                    response_data = {
                        "system": system,
                        "response": response,
                        "phase": "initial"  # 互換性のためにphaseを追加
                    }
                    print(f"クライアントに送信するデータ (ストリームモード): {response_data}")
                    await websocket.send_json(response_data)

                # ストリーミングレスポンスを生成
                async for response in chat_model.get_response_streaming(
                    messages, send_update
                ):
                    # すでにコールバックで処理されているので、ここでは何もしない
                    pass

            else:
                # 非ストリーミング、非討論モードの場合
                response = await chat_model.get_response(messages)
                response_data = {"system": "consensus", "response": response, "phase": "final"}
                print(f"クライアントに送信するデータ (非ストリーム): {response_data}")
                await websocket.send_json(response_data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# アプリケーションを実行する関数
def run_app(
    host: str = "0.0.0.0",
    port: int = 8000,
    api_base: str | None = None,
    model: str | None = None,
    api_type: str = "ollama"
):
    """APIサーバーを実行する.

    Args:
        host: サーバーのホスト
        port: サーバーのポート
        api_base: LLM APIのベースURL
        model: 使用するモデル名
        api_type: APIの種類("ollama"または"litellm")

    """
    import uvicorn

    # グローバル設定
    global _API_BASE, _MODEL, _API_TYPE
    _API_BASE = api_base or "http://localhost:11434/api"  # デフォルト値を保証
    _MODEL = model or "phi4-mini"  # デフォルト値を保証
    _API_TYPE = api_type

    # サーバー起動
    uvicorn.run(app, host=host, port=port)
