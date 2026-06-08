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
import AdminPage from "./pages/AdminPage";
import Header from "./components/common/Header";
import Footer from "./components/common/Footer";
import { googleLogin } from "./api/auth";
import { URL } from "./constants";
import { isAdminRole } from "./utils/auth";

import "./css/index.css";
import "./css/App.css";

const authStorageKey = "logoGuard:isLoggedIn";
const googleTokenStorageKey = "logoGuard:googleToken";
const userRoleStorageKey = "logoGuard:userRole";

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

function AdminRouteGuard({ isLoggedIn, isAdmin }) {
  useEffect(() => {
    if (!isLoggedIn) {
      alert("로그인이 필요한 서비스 입니다.");
      return;
    }

    if (!isAdmin) {
      alert("관리자 권한이 필요합니다.");
    }
  }, [isLoggedIn, isAdmin]);

  if (!isLoggedIn || !isAdmin) {
    return <Navigate to={URL.HOME} replace />;
  }

  return <AdminPage />;
}

function SiteLayout({ isLoggedIn, userRole, onGoogleLogin, onLogout }) {
  return (
    <div className="app-shell">
      <Header
        isLoggedIn={isLoggedIn}
        userRole={userRole}
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
    return window.localStorage.getItem(googleTokenStorageKey) || "";
  });
  const [userRole, setUserRole] = useState(() => {
    return window.localStorage.getItem(userRoleStorageKey) || "";
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
      window.localStorage.setItem(googleTokenStorageKey, googleToken);
      return;
    }

    window.localStorage.removeItem(googleTokenStorageKey);
  }, [googleToken]);

  useEffect(() => {
    if (userRole) {
      window.localStorage.setItem(userRoleStorageKey, userRole);
      return;
    }

    window.localStorage.removeItem(userRoleStorageKey);
  }, [userRole]);

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

      const result = await googleLogin({
        token: credentialResponse.credential,
      });
      console.log("Google login API response:", result);
      setGoogleToken(credentialResponse.credential);
      setUserRole(result?.role || "");
      setIsLoggedIn(true);
    } catch (error) {
      console.error("Google login API failed:", error);
      alert("API 요청에 실패하였습니다. 잠시후 시도해주세요.");
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setGoogleToken("");
    setUserRole("");
  };

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  const isAdmin = isAdminRole(userRole);

  const appContent = (
    <BrowserRouter>
      <Routes>
        <Route
          element={
            <SiteLayout
              isLoggedIn={isLoggedIn}
              userRole={userRole}
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
            path="/admin"
            element={
              <AdminRouteGuard isLoggedIn={isLoggedIn} isAdmin={isAdmin} />
            }
          />
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
