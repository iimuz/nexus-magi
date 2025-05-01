// MAGIシステム APIとの通信を担当するサービス

import { OpenAPI } from '../generated-api';
import { MagiWebSocketClient, WebSocketOptions, WebSocketConnection } from './websocketClient';

// APIサーバーのベースURL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// OpenAPIクライアントの設定
OpenAPI.BASE = API_BASE_URL;

// WebSocket接続を確立し、メッセージの送受信を行う
// @returns WebSocket接続の制御オブジェクト
export const connectToWebSocket = (options: WebSocketOptions): WebSocketConnection => {
  return MagiWebSocketClient.connect(options);
};
