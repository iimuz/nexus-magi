import React from "react";
import ReactDOM from "react-dom/client";
import {
  CssBaseline,
  ThemeProvider,
  createTheme,
} from "@mui/material";
import App from "./App.tsx";

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
