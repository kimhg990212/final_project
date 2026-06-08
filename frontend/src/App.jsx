import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
} from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";

import Home from "./pages/Home";
import TrendPage from "./pages/TrendPage";
import DetectPage from "./pages/DetectPage";
import GeneratePage from "./pages/GeneratePage";
import MyPage from "./pages/MyPage";
import Header from "./components/common/Header";
import Footer from "./components/common/Footer";
import { googleLogin } from "./api/auth";
import { URL } from "./constants";

import "./css/index.css";
import "./css/App.css";

const authStorageKey = "logoGuard:isLoggedIn";

function DetectRouteGuard({ isLoggedIn }) {
  useEffect(() => {
    if (!isLoggedIn) {
      alert("로그인이 필요한 서비스 입니다.");
    }
  }, [isLoggedIn]);

  if (!isLoggedIn) {
    return <Navigate to={URL.HOME} replace />;
  }

  return <DetectPage />;
}

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
  const [googleToken, setGoogleToken] = useState(() => {
    return window.localStorage.getItem("logoGuard:googleToken") || "";
  });

  useEffect(() => {
    if (isLoggedIn) {
      window.localStorage.setItem(authStorageKey, "true");
      return;
    }

    window.localStorage.removeItem(authStorageKey);
  }, [isLoggedIn]);

  useEffect(() => {
    if (googleToken) {
      window.localStorage.setItem("logoGuard:googleToken", googleToken);
      return;
    }

    window.localStorage.removeItem("logoGuard:googleToken");
  }, [googleToken]);

  const handleGoogleLogin = async (credentialResponse) => {
    console.log("Google credential response:", credentialResponse);
    console.log("Google credential token:", credentialResponse?.credential);
    if (!credentialResponse?.credential) {
      alert("API 요청에 실패하였습니다. 잠시후 시도해주세요.");
      return;
    }

    try {
      const decoded = jwtDecode(credentialResponse.credential);
      console.log("Decoded Google credential:", decoded);

      const result = await googleLogin({ token: credentialResponse.credential });
      console.log("Google login API response:", result);
      setGoogleToken(credentialResponse.credential);
      setIsLoggedIn(true);
    } catch (error) {
      console.error("Google login API failed:", error);
      alert("API 요청에 실패하였습니다. 잠시후 시도해주세요.");
    }
  };
  const handleLogout = () => {
    setIsLoggedIn(false);
    setGoogleToken("");
  };
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
          <Route
            path="/detect"
            element={<DetectRouteGuard isLoggedIn={isLoggedIn} />}
          />
          <Route path={URL.GENERATE} element={<GeneratePage />} />
            <Route
            path={URL.MYPAGE}
            element={
              isLoggedIn ? (
                <MyPage
                  onDeleteAccount={handleLogout}
                  googleToken={googleToken}
                />
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
