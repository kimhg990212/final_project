import { NavLink } from "react-router-dom";
import "../../css/common/header.css";
import { URL } from "../../constants";

function Header({ isLoggedIn, onLogin, onSignup, onLogout }) {
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
            <>
              <button
                type="button"
                className="header-auth-link secondary"
                onClick={onSignup}
              >
                회원가입
              </button>
              <button
                type="button"
                className="header-auth-link primary"
                onClick={onLogin}
              >
                로그인
              </button>
            </>
          ) : (
            <>
              <span className="header-user-chip">로그인됨</span>
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
