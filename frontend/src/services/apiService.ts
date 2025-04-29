// MAGIシステム APIとの通信を担当するサービス

// メッセージの型定義
interface Message {
  role: "user" | "assistant";
  content: string;
}

// WebSocket接続オプションの型定義
interface WebSocketOptions {
  messages: Message[];
  debate?: boolean;
  debateRounds?: number;
  onMelchiorResponse?: (response: string, phase?: string) => void;
  onBalthasarResponse?: (response: string, phase?: string) => void;
  onCasperResponse?: (response: string, phase?: string) => void;
  onConsensusResponse?: (response: string, phase?: string) => void;
  onError?: (error: Error) => void;
}

// WebSocketからの応答データの型定義
interface WebSocketResponse {
  system: "melchior" | "balthasar" | "casper" | "consensus";
  response: string;
  phase?: string;
}

// WebSocket接続制御オブジェクトの型定義
interface WebSocketConnection {
  close: () => void;
}

// APIサーバーのベースURL
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// WebSocket接続を確立し、メッセージの送受信を行う
// @returns WebSocket接続の制御オブジェクト
export const connectToWebSocket = ({
  messages,
  debate = true,
  debateRounds = 1,
  onMelchiorResponse,
  onBalthasarResponse,
  onCasperResponse,
  onConsensusResponse,
  onError,
}: WebSocketOptions): WebSocketConnection => {
  // WebSocketの生成
  const socket = new WebSocket(
    `${API_BASE_URL.replace("http", "ws")}/api/chat/ws`,
  );

  // 接続オープン時のハンドラ
  socket.onopen = () => {
    console.log("WebSocket接続が確立されました");

    // リクエストデータをログ出力
    const requestData = {
      messages,
      stream: true,
      debate,
      debate_rounds: debateRounds,
    };
    console.log("送信データ:", requestData);

    // メッセージ送信
    socket.send(JSON.stringify(requestData));
  };

  // メッセージ受信時のハンドラ
  socket.onmessage = (event: MessageEvent) => {
    try {
      console.log("WebSocketから受信したデータ:", event.data);
      const data = JSON.parse(event.data) as WebSocketResponse;
      console.log("パースしたデータ:", data);

      // システムごとの応答を処理
      if (data.system === "melchior") {
        console.log("MELCHIORの応答を処理:", data.response, data.phase);
        onMelchiorResponse && onMelchiorResponse(data.response, data.phase);
      } else if (data.system === "balthasar") {
        console.log("BALTHASARの応答を処理:", data.response, data.phase);
        onBalthasarResponse && onBalthasarResponse(data.response, data.phase);
      } else if (data.system === "casper") {
        console.log("CASPERの応答を処理:", data.response, data.phase);
        onCasperResponse && onCasperResponse(data.response, data.phase);
      } else if (data.system === "consensus") {
        console.log("最終合議結果を処理:", data.response, data.phase);
        onConsensusResponse && onConsensusResponse(data.response, data.phase);
      } else {
        console.warn("不明なシステムからの応答:", data);
      }
    } catch (error) {
      console.error(
        "WebSocketメッセージの処理中にエラーが発生しました:",
        error,
      );
      console.error("受信したデータ:", event.data);
      onError &&
        onError(error instanceof Error ? error : new Error(String(error)));
    }
  };

  // エラー時のハンドラ
  socket.onerror = (error: Event) => {
    console.error("WebSocket接続エラー:", error);
    onError && onError(new Error("WebSocket connection error"));
  };

  // 接続クローズ時のハンドラ
  socket.onclose = (event: CloseEvent) => {
    console.log("WebSocket接続がクローズされました:", event.code, event.reason);
  };

  // 接続の制御オブジェクトを返す
  return {
    close: () => {
      socket.close();
    },
  };
};
