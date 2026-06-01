// import { StrictMode } from "react";  // 보통 main.jsx에서 StrictMode를 쓰니까 App.jsx에선 필요 없음
import { Routes, Route, Navigate } from "react-router-dom";
import { BrowserRouter } from "react-router-dom";

import Home from "./pages/Home";
import TrendPage from "./pages/TrendPage";

import GeneratePage from "./pages/GeneratePage";

/* css */
import "./css/index.css";
import "./css/App.css";
import { URL } from "./constants";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path={URL.HOME} element={<Home />} />
        <Route path={URL.TREND} element={<TrendPage />} />

        <Route path={URL.GENERATE} element={<GeneratePage />} />

        <Route path="*" element={<Navigate to={URL.HOME} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
