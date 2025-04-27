import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import ReactMarkdown from 'react-markdown';

/**
 * チャットメッセージを表示するコンポーネント
 * @param {Object} props
 * @param {string} props.role - メッセージの送信者 ('user' または 'assistant')
 * @param {string} props.content - メッセージの内容
 */
const MessageBubble = ({ role, content }) => {
  const isUser = role === 'user';

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
        width: '100%'
      }}
    >
      <Paper
        elevation={1}
        sx={{
          p: 2,
          maxWidth: '80%',
          backgroundColor: isUser ? '#1976d2' : '#f5f5f5',
          color: isUser ? 'white' : 'black',
          borderRadius: 2
        }}
      >
        <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
          {isUser ? 'あなた' : 'MAGI System'}
        </Typography>
        <ReactMarkdown>{content}</ReactMarkdown>
      </Paper>
    </Box>
  );
};

export default MessageBubble;
