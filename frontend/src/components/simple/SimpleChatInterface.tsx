// シンプルチャットインターフェイスコンポーネント
import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  Container,
  TextField,
  Button,
  Paper,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import MessageBubble from "../MessageBubble.tsx";
import { connectToWebSocket } from "../../services/apiService.ts";

// メッセージの型定義
interface Message {
  role: "user" | "assistant";
  content: string;
}

const SimpleChatInterface: React.FC = () => {
  // メッセージリストの状態
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "こんにちは！シンプルチャットモードです。どのようなご質問がありますか？",
    },
  ]);

  // 入力テキストの状態
  const [inputText, setInputText] = useState<string>("");

  // 送信中の状態
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // WebSocket接続オブジェクト
  const wsConnectionRef = useRef<WebSocket | null>(null);

  // メッセージリストの参照
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // メッセージが追加されたときに自動スクロール
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // 入力テキストの変更ハンドラ
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputText(e.target.value);
  };

  // フォーム送信ハンドラ
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputText.trim() || isSubmitting) return;

    console.log("メッセージ送信開始:", inputText);

    // ユーザーメッセージを追加
    const newMessages: Message[] = [
      ...messages,
      { role: "user", content: inputText },
    ];
    setMessages(newMessages);
    console.log("メッセージリスト更新:", newMessages);

    // 入力をクリア
    setInputText("");

    // 送信中フラグを設定
    setIsSubmitting(true);

    // 以前のWebSocket接続があれば閉じる
    if (wsConnectionRef.current) {
      console.log("既存のWebSocket接続を閉じる");
      wsConnectionRef.current.close();
    }

    // WebSocketに接続（シンプルモード用のエンドポイント）
    console.log("WebSocket接続を開始");
    wsConnectionRef.current = connectToWebSocket({
      messages: newMessages,
      debate: false, // シンプルモード
      onMelchiorResponse: (response: string) => {
        // シンプルモードではMelchiorのコールバックに応答が来るが、
        // 実際にはシンプルな単一の応答
        console.log("シンプルモードからの応答を受信:", response);

        // アシスタントのメッセージを追加
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: response },
        ]);

        // 送信中フラグをリセット
        setIsSubmitting(false);
      },
      onError: (error: Error) => {
        console.error("WebSocket Error:", error);
        setIsSubmitting(false);

        // エラーメッセージをアシスタントメッセージとして追加
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `エラーが発生しました: ${error.message}` },
        ]);
      },
    });
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* メッセージエリア */}
      <Box
        sx={{ flexGrow: 1, overflow: "auto", p: 2, backgroundColor: "#f5f5f5" }}
      >
        <Container maxWidth="md">
          {/* メッセージの表示 */}
          {messages.map((message, index) => (
            <MessageBubble
              key={`msg-${index}`}
              role={message.role}
              content={message.content}
            />
          ))}
          <div ref={messagesEndRef} />
        </Container>
      </Box>

      {/* 入力エリア */}
      <Paper elevation={3} sx={{ p: 2 }}>
        <Container maxWidth="md">
          <form onSubmit={handleSubmit}>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="メッセージを入力してください..."
                value={inputText}
                onChange={handleInputChange}
                disabled={isSubmitting}
                sx={{ mr: 1 }}
              />
              <Button
                variant="contained"
                color="primary"
                endIcon={<SendIcon />}
                type="submit"
                disabled={isSubmitting || !inputText.trim()}
              >
                送信
              </Button>
            </Box>
          </form>
        </Container>
      </Paper>
    </Box>
  );
};

export default SimpleChatInterface;
