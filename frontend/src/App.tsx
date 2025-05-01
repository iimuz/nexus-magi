import React, { useState } from 'react';
import { AppBar, Toolbar, Typography, Box, Tabs, Tab } from '@mui/material';
import SimpleChatInterface from './components/simple/SimpleChatInterface.tsx';
import DebateChatInterface from './components/debate/DebateChatInterface.tsx';
import TabPanel from './components/TabPanel.tsx';

// メイン App コンポーネント
const App: React.FC = () => {
  // 現在のタブ状態
  const [currentTab, setCurrentTab] = useState(0);

  // タブ変更ハンドラ
  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* ヘッダー */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Nexus MAGI
          </Typography>
        </Toolbar>
        <Tabs value={currentTab} onChange={handleTabChange} aria-label="chat mode tabs" centered>
          <Tab label="シンプルモード" />
          <Tab label="討論モード" />
        </Tabs>
      </AppBar>

      {/* タブコンテンツ */}
      <TabPanel value={currentTab} index={0}>
        <SimpleChatInterface />
      </TabPanel>
      <TabPanel value={currentTab} index={1}>
        <DebateChatInterface />
      </TabPanel>
    </Box>
  );
};

export default App;
