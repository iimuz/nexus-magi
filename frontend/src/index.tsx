import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import {
  CssBaseline,
  ThemeProvider,
  createTheme,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Tabs,
  Tab,
  useMediaQuery,
} from "@mui/material";
import SimpleChatInterface from "./components/simple/SimpleChatInterface.tsx";
import DebateChatInterface from "./components/debate/DebateChatInterface.tsx";

// ダークテーマを作成
const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#7B68EE", // ミディアムスレートブルー
    },
    secondary: {
      main: "#D63AF9", // 紫がかったピンク
    },
    background: {
      default: "#1E1E2F", // ダークブルーなバックグラウンド
      paper: "#2D2D44", // もう少し明るいシェード
    },
  },
  typography: {
    fontFamily: [
      "-apple-system",
      "BlinkMacSystemFont",
      '"Segoe UI"',
      "Roboto",
      '"Helvetica Neue"',
      "Arial",
      "sans-serif",
    ].join(","),
  },
});

// タブパネルコンポーネント
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      style={{ height: "calc(100vh - 112px)" }}
      {...other}
    >
      {value === index && (
        <Box sx={{ height: "100%" }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// メイン App コンポーネント
const App: React.FC = () => {
  // 現在のタブ状態
  const [currentTab, setCurrentTab] = useState(0);

  // タブ変更ハンドラ
  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* ヘッダー */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Nexus MAGI
          </Typography>
        </Toolbar>
        <Tabs
          value={currentTab}
          onChange={handleTabChange}
          aria-label="chat mode tabs"
          centered
        >
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

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement,
);
root.render(
  <React.StrictMode>
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>,
);
