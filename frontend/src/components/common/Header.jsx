import { useState } from "react";
import { NavLink } from "react-router-dom";

import { URL } from "../../constants";
import { login, logout } from "../../api/auth";
import "../../css/common/header.css";

function Header() {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("user");
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [showLoginModal, setShowLoginModal] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const isLoggedIn = !!user;

  const navItems = [
    { to: URL.TREND, label: "트렌드" },
    { to: "/detect", label: "유사 검색" },
    { to: URL.GENERATE, label: "로고 생성" },
    ...(isLoggedIn ? [{ to: URL.MYPAGE, label: "마이페이지" }] : []),
  ];

  const handleLogin = async () => {
    try {
      const data = await login({ email, password });

      const loginUser = {
        id: data.user_id,
        email: data.email,
        nickname: data.nickname,
        role: data.role,
      };

      localStorage.setItem("user", JSON.stringify(loginUser));
      setUser(loginUser);
      setShowLoginModal(false);
      setEmail("");
      setPassword("");

      alert("로그인 성공!");
    } catch (err) {
      alert(err.message);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();

      localStorage.removeItem("user");
      setUser(null);

      alert("로그아웃 되었습니다.");
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <>
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
              <button
                type="button"
                className="header-auth-link primary"
                onClick={() => setShowLoginModal(true)}
              >
                로그인
              </button>
            ) : (
              <>
                <span className="header-user-chip">{user.nickname}님</span>

                {user.role === "ADMIN" && (
                  <NavLink to="/admin" className="header-auth-link secondary">
                    관리자
                  </NavLink>
                )}

                <button
                  type="button"
                  className="header-auth-link secondary"
                  onClick={handleLogout}
                >
                  로그아웃
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {showLoginModal && (
        <div className="login-modal">
          <div className="login-box">
            <h2>로그인</h2>

            <input
              type="email"
              placeholder="이메일"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <input
              type="password"
              placeholder="비밀번호"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleLogin();
                }
              }}
            />

            <button type="button" onClick={handleLogin}>
              로그인
            </button>
            <button
              type="button"
              className="google-login-btn"
              onClick={() => {
                // 나중에 언니가 구글 로그인 연결
              }}
            >
              <img
                src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                alt="google"
              />
              Google로 로그인
            </button>
            <button
              type="button"
              className="login-close-btn"
              onClick={() => setShowLoginModal(false)}
            >
              닫기
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default Header;
