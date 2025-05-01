import { OpenAPI, ChatMessage, ChatRequest, WebSocketResponse } from '../generated-api';

/**
 * WebSocket接続オプションのインターフェース
 */
export interface WebSocketOptions {
  messages: ChatMessage[];
  debate?: boolean;
  debateRounds?: number;
  onMelchiorResponse?: (response: string, phase?: string) => void;
  onBalthasarResponse?: (response: string, phase?: string) => void;
  onCasperResponse?: (response: string, phase?: string) => void;
  onConsensusResponse?: (response: string, phase?: string) => void;
  onError?: (error: Error) => void;
}

/**
 * WebSocket接続制御オブジェクトのインターフェース
 */
export interface WebSocketConnection {
  close: () => void;
}

/**
 * MAGIシステムのWebSocket API クライアント
 */
export class MagiWebSocketClient {
  /**
   * WebSocket接続を確立し、メッセージの送受信を行う
   * @param options WebSocket接続オプション
   * @returns WebSocket接続の制御オブジェクト
   */
  public static connect(options: WebSocketOptions): WebSocketConnection {
    const {
      messages,
      debate = true,
      debateRounds = 1,
      onMelchiorResponse,
      onBalthasarResponse,
      onCasperResponse,
      onConsensusResponse,
      onError,
    } = options;

    // WebSocketエンドポイントの決定
    const wsEndpoint = debate ? '/api/debate/ws' : '/api/chat/ws';
    const baseUrl = OpenAPI.BASE || 'http://localhost:8000';
    const wsUrl = `${baseUrl.replace('http', 'ws')}${wsEndpoint}`;

    // WebSocketの生成
    const socket = new WebSocket(wsUrl);

    // 接続オープン時のハンドラ
    socket.onopen = () => {
      console.log('WebSocket接続が確立されました');

      // リクエストデータの生成
      const requestData: ChatRequest = {
        messages,
        stream: true,
        debate,
        debate_rounds: debateRounds,
      };
      console.log('送信データ:', requestData);

      // メッセージ送信
      socket.send(JSON.stringify(requestData));
    };

    // メッセージ受信時のハンドラ
    socket.onmessage = (event: MessageEvent) => {
      try {
        console.log('WebSocketから受信したデータ:', event.data);
        const data = JSON.parse(event.data) as WebSocketResponse;
        console.log('パースしたデータ:', data);

        // システムごとの応答を処理
        if (data.system === 'melchior') {
          console.log('MELCHIORの応答を処理:', data.response, data.phase);
          if (onMelchiorResponse) {
            onMelchiorResponse(data.response, data.phase);
          }
        } else if (data.system === 'balthasar') {
          console.log('BALTHASARの応答を処理:', data.response, data.phase);
          if (onBalthasarResponse) {
            onBalthasarResponse(data.response, data.phase);
          }
        } else if (data.system === 'casper') {
          console.log('CASPERの応答を処理:', data.response, data.phase);
          if (onCasperResponse) {
            onCasperResponse(data.response, data.phase);
          }
        } else if (data.system === 'consensus') {
          console.log('最終合議結果を処理:', data.response, data.phase);
          if (onConsensusResponse) {
            onConsensusResponse(data.response, data.phase);
          }
        } else {
          console.warn('不明なシステムからの応答:', data);
        }
      } catch (error) {
        console.error('WebSocketメッセージの処理中にエラーが発生しました:', error);
        console.error('受信したデータ:', event.data);
        if (onError) {
          onError(error instanceof Error ? error : new Error(String(error)));
        }
      }
    };

    // エラー時のハンドラ
    socket.onerror = (error: Event) => {
      console.error('WebSocket接続エラー:', error);
      if (onError) {
        onError(new Error('WebSocket connection error'));
      }
    };

    // 接続クローズ時のハンドラ
    socket.onclose = (event: CloseEvent) => {
      console.log('WebSocket接続がクローズされました:', event.code, event.reason);
    };

    // 接続の制御オブジェクトを返す
    return {
      close: () => {
        socket.close();
      },
    };
  }
}
