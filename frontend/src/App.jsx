import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
} from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";

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

function SiteLayout({ isLoggedIn, onGoogleLogin, onLogout }) {
  return (
    <div className="app-shell">
      <Header
        isLoggedIn={isLoggedIn}
        onGoogleLogin={onGoogleLogin}
        onLogout={onLogout}
        googleClientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}
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

  const handleGoogleLogin = (credentialResponse) => {
    console.log("Google credential response:", credentialResponse);
    console.log("Google credential token:", credentialResponse?.credential);
    setIsLoggedIn(true);
  };
  const handleLogout = () => setIsLoggedIn(false);
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  const appContent = (
    <BrowserRouter>
      <Routes>
        <Route
          element={
            <SiteLayout
              isLoggedIn={isLoggedIn}
              onGoogleLogin={handleGoogleLogin}
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

  if (!googleClientId) {
    return appContent;
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      {appContent}
    </GoogleOAuthProvider>
  );
}

export default App;
