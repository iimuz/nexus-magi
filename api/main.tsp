import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";

using TypeSpec.Http;
using TypeSpec.Rest;

@service
@doc("MAGIシステムによるチャットAPI")
namespace NexusMagi {
  // 基本的なモデル定義
  model ChatMessage {
    @doc("メッセージの役割（ユーザーまたはアシスタント）")
    role: "user" | "assistant";

    @doc("メッセージの内容")
    content: string;
  }

  // チャットリクエストモデル
  model ChatRequest {
    @doc("メッセージの履歴")
    messages: ChatMessage[];

    @doc("ストリーミングモードを使用するかどうか")
    stream?: boolean = false;

    @doc("討論モードを使用するかどうか")
    debate?: boolean = false;

    @doc("討論ラウンド数")
    debate_rounds?: int32 = 1;
  }

  // WebSocketレスポンスモデル
  model WebSocketResponse {
    @doc("レスポンスを生成するシステム（MAGI）")
    system: "melchior" | "balthasar" | "casper" | "consensus";

    @doc("レスポンスの内容")
    response: string;

    @doc("現在のフェーズ")
    phase?: string;
  }

  // WebSocketクライアントインターフェース用のカスタムX-Tags
  @route("/api")
  namespace Api {
    @route("/chat")
    namespace Chat {
      @doc("WebSocketチャットエンドポイント")
      @route("/ws")
      @tag("x-websocket")
      op websocketChat(request: ChatRequest): WebSocketResponse;
    }

    @route("/debate")
    namespace Debate {
      @doc("WebSocket討論チャットエンドポイント")
      @route("/ws")
      @tag("x-websocket")
      op websocketDebate(request: ChatRequest): WebSocketResponse;
    }
  }
}
