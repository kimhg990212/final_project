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
const userIdStorageKey = "logoGuard:userId";
const userNicknameStorageKey = "logoGuard:userNickname";
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

function RequireLogin({ isLoggedIn, children }) {
  useEffect(() => {
    if (!isLoggedIn) {
      alert("로그인이 필요한 서비스 입니다.");
    }
  }, [isLoggedIn]);

  if (!isLoggedIn) {
    return <Navigate to={URL.HOME} replace />;
  }

  return children;
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

  if (!isLoggedIn) {
    return <Navigate to={URL.HOME} replace />;
  }

  if (!isAdmin) {
    return <Navigate to={URL.HOME} replace />;
  }

  return <AdminPage />;
}

function SiteLayout({
  isLoggedIn,
  userNickname,
  userRole,
  onGoogleLogin,
  onLogout,
}) {
  return (
    <div className="app-shell">
      <Header
        isLoggedIn={isLoggedIn}
        userNickname={userNickname}
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
  const [userId, setUserId] = useState(() => {
    const storedUserId = window.localStorage.getItem(userIdStorageKey);
    return storedUserId ? Number(storedUserId) : null;
  });
  const [userNickname, setUserNickname] = useState(() => {
    return window.localStorage.getItem(userNicknameStorageKey) || "";
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
    if (userId) {
      window.localStorage.setItem(userIdStorageKey, String(userId));
      return;
    }

    window.localStorage.removeItem(userIdStorageKey);
  }, [userId]);

  useEffect(() => {
    if (userNickname) {
      window.localStorage.setItem(userNicknameStorageKey, userNickname);
      return;
    }

    window.localStorage.removeItem(userNicknameStorageKey);
  }, [userNickname]);

  useEffect(() => {
    if (userRole) {
      window.localStorage.setItem(userRoleStorageKey, userRole);
      return;
    }

    window.localStorage.removeItem(userRoleStorageKey);
  }, [userRole]);

  const handleGoogleLogin = async (credentialResponse) => {
    // console.log("Google credential response:", credentialResponse);
    // console.log("Google credential token:", credentialResponse?.credential);
    if (!credentialResponse?.credential) {
      alert("API 요청에 실패하였습니다. 잠시후 시도해주세요.");
      return;
    }

    try {
      const decoded = jwtDecode(credentialResponse.credential);
      // console.log("Decoded Google credential:", decoded);

      const result = await googleLogin({
        token: credentialResponse.credential,
      });

      console.log("Google login API response:", result);
      setGoogleToken(credentialResponse.credential);
      setUserId(result?.user_id ?? null);
      setUserNickname(result?.nickname || "");
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
    setUserId(null);
    setUserNickname("");
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
              userNickname={userNickname}
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
          <Route
            path={URL.GENERATE}
            element={
              <RequireLogin isLoggedIn={isLoggedIn}>
                <GeneratePage userId={userId} />
              </RequireLogin>
            }
          />
          <Route
            path="/admin"
            element={
              isLoggedIn ? (
                isAdmin ? (
                  <AdminPage />
                ) : (
                  <Navigate to={URL.HOME} replace />
                )
              ) : (
                <Navigate to={URL.HOME} replace />
              )
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
