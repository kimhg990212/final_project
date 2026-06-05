import { NavLink } from "react-router-dom";

import { URL } from "../../constants";
import "../../css/common/header.css";

import { GoogleLogin } from "@react-oauth/google";

function Header({ isLoggedIn, onGoogleLogin, onLogout, googleClientId }) {
  const navItems = [
    { to: URL.TREND, label: "트렌드" },
    { to: "/detect", label: "유사 검색" },
    { to: URL.GENERATE, label: "로고 생성" },
    ...(isLoggedIn ? [{ to: URL.MYPAGE, label: "마이페이지" }] : []),
  ];

  return (
    <header className="common-header">
      <NavLink to={URL.HOME} className="header-logo">
        Mark Lab
      </NavLink>

      <div className="header-right">
        <nav className="header-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `header-nav-link${isActive ? " active" : ""}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="header-auth">
          {!isLoggedIn ? (
            googleClientId ? (
              <GoogleLogin
                onSuccess={(credentialResponse) => {
                  console.log(
                    "Google credential response:",
                    credentialResponse,
                  );
                  console.log(
                    "Google credential token:",
                    credentialResponse?.credential,
                  );
                  onGoogleLogin?.(credentialResponse);
                }}
                onError={() => console.log("Google Login Failed")}
                useOneTap={false}
                shape="pill"
                theme="outline"
              />
            ) : (
              <button
                type="button"
                className="header-auth-link primary"
                disabled
                title="VITE_GOOGLE_CLIENT_ID를 설정해야 Google 로그인이 활성화됩니다"
              >
                구글 로그인 불가
              </button>
            )
          ) : (
            <>
              <span className="header-user-chip">구글 로그인됨</span>
              <button
                type="button"
                className="header-auth-link secondary"
                onClick={onLogout}
              >
                로그아웃
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
