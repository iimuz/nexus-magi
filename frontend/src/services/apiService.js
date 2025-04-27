/**
 * MAGIシステム APIとの通信を担当するサービス
 */

// APIサーバーのベースURL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

/**
 * WebSocket接続を確立し、メッセージの送受信を行う
 * @param {Object} options - 接続オプション
 * @param {Array} options.messages - 送信するメッセージ配列
 * @param {boolean} options.debate - 討論モードを使用するかどうか
 * @param {number} options.debateRounds - 討論ラウンド数
 * @param {function} options.onMelchiorResponse - Melchiorの応答を受け取るコールバック
 * @param {function} options.onBalthasarResponse - Balthasarの応答を受け取るコールバック
 * @param {function} options.onCasperResponse - Casperの応答を受け取るコールバック
 * @param {function} options.onConsensusResponse - 最終合議結果を受け取るコールバック
 * @param {function} options.onError - エラー発生時のコールバック
 * @returns {Object} WebSocket接続の制御オブジェクト
 */
export const connectToWebSocket = ({
  messages,
  debate = true,
  debateRounds = 1,
  onMelchiorResponse,
  onBalthasarResponse,
  onCasperResponse,
  onConsensusResponse,
  onError
}) => {
  // WebSocketの生成
  const socket = new WebSocket(`${API_BASE_URL.replace('http', 'ws')}/api/chat/ws`);

  // 接続オープン時のハンドラ
  socket.onopen = () => {
    console.log('WebSocket接続が確立されました');

    // リクエストデータをログ出力
    const requestData = {
      messages,
      stream: true,
      debate,
      debate_rounds: debateRounds
    };
    console.log('送信データ:', requestData);

    // メッセージ送信
    socket.send(JSON.stringify(requestData));
  };

  // メッセージ受信時のハンドラ
  socket.onmessage = (event) => {
    try {
      console.log('WebSocketから受信したデータ:', event.data);
      const data = JSON.parse(event.data);
      console.log('パースしたデータ:', data);

      // システムごとの応答を処理
      if (data.system === 'melchior') {
        console.log('MELCHIORの応答を処理:', data.response, data.phase);
        onMelchiorResponse && onMelchiorResponse(data.response, data.phase);
      } else if (data.system === 'balthasar') {
        console.log('BALTHASARの応答を処理:', data.response, data.phase);
        onBalthasarResponse && onBalthasarResponse(data.response, data.phase);
      } else if (data.system === 'casper') {
        console.log('CASPERの応答を処理:', data.response, data.phase);
        onCasperResponse && onCasperResponse(data.response, data.phase);
      } else if (data.system === 'consensus') {
        console.log('最終合議結果を処理:', data.response, data.phase);
        onConsensusResponse && onConsensusResponse(data.response, data.phase);
      } else {
        console.warn('不明なシステムからの応答:', data);
      }
    } catch (error) {
      console.error('WebSocketメッセージの処理中にエラーが発生しました:', error);
      console.error('受信したデータ:', event.data);
      onError && onError(error);
    }
  };

  // エラー時のハンドラ
  socket.onerror = (error) => {
    console.error('WebSocket接続エラー:', error);
    onError && onError(error);
  };

  // 接続クローズ時のハンドラ
  socket.onclose = (event) => {
    console.log('WebSocket接続がクローズされました:', event.code, event.reason);
  };

  // 接続の制御オブジェクトを返す
  return {
    close: () => {
      socket.close();
    }
  };
};

/**
 * 通常のHTTP APIを使ってチャットメッセージを送信（非ストリーミングモード）
 * @param {Array} messages - 送信するメッセージ配列
 * @returns {Promise} レスポンスを返すPromise
 */
export const sendChatMessage = async (messages) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        stream: false,
        debate: false
      }),
    });

    if (!response.ok) {
      throw new Error(`APIエラー: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('チャットメッセージの送信中にエラーが発生しました:', error);
    throw error;
  }
};
