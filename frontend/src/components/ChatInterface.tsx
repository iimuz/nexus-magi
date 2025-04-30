import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  Container,
  TextField,
  Button,
  Typography,
  AppBar,
  Toolbar,
  FormControlLabel,
  Switch,
  Paper,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import MessageBubble from "./MessageBubble.tsx";
import MagiSystemResponse from "./MagiSystemResponse.tsx";
import { connectToWebSocket } from "../services/apiService.ts";

// メッセージの型定義
interface Message {
  role: "user" | "assistant";
  content: string;
}

// MAGIシステムの応答の型定義
interface MagiResponseState {
  melchior: string;
  balthasar: string;
  casper: string;
  consensus: string;
  phase: "initial" | "thinking" | "debating" | "final";
}

const ChatInterface: React.FC = () => {
  // メッセージリストの状態
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "こんにちは！MAGI合議システムです。どのようなご質問がありますか？",
    },
  ]);

  // 入力テキストの状態
  const [inputText, setInputText] = useState<string>("");

  // 送信中の状態
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // MAGIシステムの応答状態
  const [magiResponse, setMagiResponse] = useState<MagiResponseState>({
    melchior: "応答待ち...",
    balthasar: "応答待ち...",
    casper: "応答待ち...",
    consensus: "",
    phase: "initial",
  });

  // MAGIシステムメッセージのID
  const [magiMessageId, setMagiMessageId] = useState<number | null>(null);

  // WebSocket接続オブジェクト
  const wsConnectionRef = useRef<WebSocket | null>(null);

  // 討論モードの状態
  const [debateMode, setDebateMode] = useState<boolean>(true);

  // 討論ラウンド数
  const [debateRounds, setDebateRounds] = useState<number>(1);

  // メッセージリストの参照
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // メッセージが追加されたときに自動スクロール
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, magiResponse]);

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

    // MAGI合議システムの応答状態をリセット
    setMagiResponse({
      melchior: "応答待ち...",
      balthasar: "応答待ち...",
      casper: "応答待ち...",
      consensus: "",
      phase: "initial",
    });
    console.log("MAGIレスポンス状態リセット");

    // MAGIシステムメッセージのIDをリセット
    setMagiMessageId(newMessages.length);
    console.log("MAGIメッセージID設定:", newMessages.length);

    // 送信中フラグを設定
    setIsSubmitting(true);

    // 以前のWebSocket接続があれば閉じる
    if (wsConnectionRef.current) {
      console.log("既存のWebSocket接続を閉じる");
      wsConnectionRef.current.close();
    }

    // WebSocketに接続
    console.log("WebSocket接続を開始");
    wsConnectionRef.current = connectToWebSocket({
      messages: newMessages,
      debate: debateMode, // 討論モードの設定によってエンドポイントが選択される
      debateRounds: debateRounds,
      onMelchiorResponse: (response: string, phase?: string) => {
        console.log("MELCHIORからの応答を受信:", response, phase);
        setMagiResponse((prev) => {
          const updated = {
            ...prev,
            melchior: response,
            phase:
              (phase as "initial" | "thinking" | "debating" | "final") ||
              prev.phase,
          };
          console.log("MELCHIORの応答で状態を更新:", updated);
          return updated;
        });
      },
      onBalthasarResponse: (response: string, phase?: string) => {
        console.log("BALTHASARからの応答を受信:", response, phase);
        setMagiResponse((prev) => {
          const updated = {
            ...prev,
            balthasar: response,
            phase:
              (phase as "initial" | "thinking" | "debating" | "final") ||
              prev.phase,
          };
          console.log("BALTHASARの応答で状態を更新:", updated);
          return updated;
        });
      },
      onCasperResponse: (response: string, phase?: string) => {
        console.log("CASPERからの応答を受信:", response, phase);
        setMagiResponse((prev) => {
          const updated = {
            ...prev,
            casper: response,
            phase:
              (phase as "initial" | "thinking" | "debating" | "final") ||
              prev.phase,
          };
          console.log("CASPERの応答で状態を更新:", updated);
          return updated;
        });
      },
      onConsensusResponse: (response: string, phase?: string) => {
        console.log("最終合議結果を受信:", response, phase);
        setMagiResponse((prev) => {
          const updated = {
            ...prev,
            consensus: response,
            phase:
              (phase as "initial" | "thinking" | "debating" | "final") ||
              "final",
          };
          console.log("最終合議結果で状態を更新:", updated);
          return updated;
        });
        setIsSubmitting(false);
      },
      onError: (error: Error) => {
        console.error("WebSocket Error:", error);
        setIsSubmitting(false);
      },
    });
  };

  // レンダリング時にデバッグ情報を出力
  useEffect(() => {
    console.log("メッセージリスト現在の状態:", messages);
    console.log("MAGIレスポンス現在の状態:", magiResponse);
    console.log("MAGIメッセージID:", magiMessageId);
  }, [messages, magiResponse, magiMessageId]);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* ヘッダー */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Nexus MAGI
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={debateMode}
                onChange={(e) => setDebateMode(e.target.checked)}
                color="default"
              />
            }
            label="討論モード"
          />
        </Toolbar>
      </AppBar>

      {/* メッセージエリア */}
      <Box
        sx={{ flexGrow: 1, overflow: "auto", p: 2, backgroundColor: "#f5f5f5" }}
      >
        <Container maxWidth="md">
          {/* メッセージの表示 */}
          {messages.map((message, index) => {
            // MAGIシステムの応答表示
            if (index === magiMessageId) {
              console.log(
                "MAGIメッセージをレンダリング - インデックス:",
                index,
              );
              return (
                <MagiSystemResponse
                  key={`magi-response-${index}`}
                  melchior={magiResponse.melchior}
                  balthasar={magiResponse.balthasar}
                  casper={magiResponse.casper}
                  consensus={magiResponse.consensus}
                  phase={magiResponse.phase}
                />
              );
            }

            // 通常のメッセージ
            console.log(
              "通常メッセージをレンダリング - インデックス:",
              index,
              "ロール:",
              message.role,
            );
            return (
              <MessageBubble
                key={`msg-${index}`}
                role={message.role}
                content={message.content}
              />
            );
          })}

          {/* magiMessageIdが設定されているが、messagesの長さ以上の場合、別途MAGIレスポンスを表示 */}
          {magiMessageId !== null && magiMessageId >= messages.length && (
            <MagiSystemResponse
              key="magi-response-extra"
              melchior={magiResponse.melchior}
              balthasar={magiResponse.balthasar}
              casper={magiResponse.casper}
              consensus={magiResponse.consensus}
              phase={magiResponse.phase}
            />
          )}
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

export default ChatInterface;
