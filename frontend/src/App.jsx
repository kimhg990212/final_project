import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
} from "react-router-dom";

import Home from "./pages/Home";
import TrendPage from "./pages/TrendPage";
import DetectPage from "./pages/DetectPage";
import GeneratePage from "./pages/GeneratePage";
import MyPage from "./pages/MyPage";
import Header from "./components/common/Header";
import Footer from "./components/common/Footer";
import { URL } from "./constants";

import "./css/index.css";
import "./css/App.css";

const authStorageKey = "logoGuard:isLoggedIn";

function SiteLayout({ isLoggedIn, onLogin, onSignup, onLogout }) {
  return (
    <div className="app-shell">
      <Header
        isLoggedIn={isLoggedIn}
        onLogin={onLogin}
        onSignup={onSignup}
        onLogout={onLogout}
      />
      <main className="app-content">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return window.localStorage.getItem(authStorageKey) === "true";
  });

  useEffect(() => {
    if (isLoggedIn) {
      window.localStorage.setItem(authStorageKey, "true");
      return;
    }

    window.localStorage.removeItem(authStorageKey);
  }, [isLoggedIn]);

  const handleLogin = () => setIsLoggedIn(true);
  const handleSignup = () => setIsLoggedIn(true);
  const handleLogout = () => setIsLoggedIn(false);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          element={
            <SiteLayout
              isLoggedIn={isLoggedIn}
              onLogin={handleLogin}
              onSignup={handleSignup}
              onLogout={handleLogout}
            />
          }
        >
          <Route path={URL.HOME} element={<Home />} />
          <Route path={URL.TREND} element={<TrendPage />} />
          <Route path="/detect" element={<DetectPage />} />
          <Route path={URL.GENERATE} element={<GeneratePage />} />
          <Route
            path={URL.MYPAGE}
            element={
              isLoggedIn ? (
                <MyPage onDeleteAccount={handleLogout} />
              ) : (
                <Navigate to={URL.HOME} replace />
              )
            }
          />
        </Route>

        <Route path="*" element={<Navigate to={URL.HOME} replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
