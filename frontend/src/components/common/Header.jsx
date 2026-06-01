import "../../css/common/header.css";

function Header() {
  return (
    <header className="common-header">
      <a href="/" className="header-logo">
        LOGO GUARD
      </a>

      <div className="header-right">
        <nav className="header-nav">
          <a href="/trends">트렌드</a>
          <a href="/detect">도용 탐지</a>
          <a href="/generate">로고 생성</a>
          <a href="/mypage">마이페이지</a>
        </nav>

        <button className="header-login-btn">로그인</button>
      </div>
    </header>
  );
}

export default Header;
