import React, { useEffect } from 'react';
import { Paper, Typography, Box, Divider, Chip } from '@mui/material';
import ReactMarkdown from 'react-markdown';

/**
 * MAGI合議システムの応答を表示するコンポーネント
 * @param {Object} props
 * @param {string} props.melchior - MELCHIORの応答
 * @param {string} props.balthasar - BALTHASARの応答
 * @param {string} props.casper - CASPERの応答
 * @param {string} props.consensus - 最終合議結果
 * @param {string} props.phase - 現在のフェーズ ('initial', 'debate_1', 'final' など)
 */
const MagiSystemResponse = ({
  melchior = '応答待ち...',
  balthasar = '応答待ち...',
  casper = '応答待ち...',
  consensus = '',
  phase = 'initial'
}) => {
  // デバッグ情報を出力
  useEffect(() => {
    console.log('MagiSystemResponseコンポーネントにプロップが届きました:');
    console.log('melchior:', melchior);
    console.log('balthasar:', balthasar);
    console.log('casper:', casper);
    console.log('consensus:', consensus);
    console.log('phase:', phase);
  }, [melchior, balthasar, casper, consensus, phase]);

  // フェーズに応じたタイトルを設定
  let phaseTitle = '';
  if (phase === 'initial') {
    phaseTitle = '初期分析';
  } else if (phase && phase.startsWith('debate_')) {
    const roundNum = phase.split('_')[1];
    phaseTitle = `討論 (ラウンド ${roundNum})`;
  } else if (phase === 'final') {
    phaseTitle = '最終判断';
  }

  return (
    <Box sx={{ mb: 2, width: '100%' }}>
      <Paper
        elevation={1}
        sx={{
          p: 2,
          backgroundColor: '#f5f5f5',
          borderRadius: 2
        }}
      >
        <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
          MAGI合議システム
          {phaseTitle && (
            <Chip
              label={phaseTitle}
              size="small"
              sx={{ ml: 1, backgroundColor: '#2a2a42', color: 'white' }}
            />
          )}
        </Typography>

        {/* MELCHIOR */}
        <Box sx={{ mb: 2, mt: 2 }}>
          <Typography
            variant="subtitle2"
            fontWeight="bold"
            sx={{ color: '#AA0000' }}
          >
            ■ MELCHIOR (科学者):
          </Typography>
          <Paper
            elevation={0}
            sx={{
              p: 1.5,
              backgroundColor: '#2a2038',
              color: '#FFD700',
              borderLeft: '4px solid #AA0000',
              my: 1
            }}
          >
            <ReactMarkdown>{melchior}</ReactMarkdown>
          </Paper>
        </Box>

        {/* BALTHASAR */}
        <Box sx={{ mb: 2 }}>
          <Typography
            variant="subtitle2"
            fontWeight="bold"
            sx={{ color: '#00AA00' }}
          >
            ■ BALTHASAR (母親):
          </Typography>
          <Paper
            elevation={0}
            sx={{
              p: 1.5,
              backgroundColor: '#1a3a2a',
              color: '#98FB98',
              borderLeft: '4px solid #00AA00',
              my: 1
            }}
          >
            <ReactMarkdown>{balthasar}</ReactMarkdown>
          </Paper>
        </Box>

        {/* CASPER */}
        <Box sx={{ mb: 2 }}>
          <Typography
            variant="subtitle2"
            fontWeight="bold"
            sx={{ color: '#0000AA' }}
          >
            ■ CASPER (女性):
          </Typography>
          <Paper
            elevation={0}
            sx={{
              p: 1.5,
              backgroundColor: '#1a2a3a',
              color: '#ADD8E6',
              borderLeft: '4px solid #0000AA',
              my: 1
            }}
          >
            <ReactMarkdown>{casper}</ReactMarkdown>
          </Paper>
        </Box>

        {/* 合議結果 */}
        {consensus && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box>
              <Typography
                variant="subtitle2"
                fontWeight="bold"
                sx={{ color: '#8888FF' }}
              >
                【最終判断】
              </Typography>
              <Paper
                elevation={0}
                sx={{
                  p: 1.5,
                  backgroundColor: '#2a2a42',
                  color: 'white',
                  borderLeft: '4px solid #8888FF',
                  my: 1
                }}
              >
                <ReactMarkdown>{consensus}</ReactMarkdown>
              </Paper>
            </Box>
          </>
        )}
      </Paper>
    </Box>
  );
};

export default MagiSystemResponse;
