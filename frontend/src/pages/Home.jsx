import { useState } from "react";
import Header from "../components/common/Header";
import Footer from "../components/common/Footer";
import "../css/Home.css";

function Home() {
  const [showLogin, setShowLogin] = useState(false);

  return (
    <div className="home-page">
      <Header />

      <section className="hero">
        <div className="hero-text">
          <span className="badge">AI Trademark & Logo Service</span>
          <h1>
            상표·로고 생성부터
            <br />
            도용 탐지까지 한 번에
          </h1>
          <p>
            자연어와 이미지를 기반으로 로고를 생성하고, 기존 상표와의 유사도를
            분석해 안전한 브랜드 제작을 돕습니다.
          </p>

          <div className="hero-actions">
            <a href="/generate" className="primary-btn">
              생성하러 가기
            </a>
            <a href="/detect" className="secondary-btn">
              도용 탐지하기
            </a>
          </div>
        </div>

        <div className="hero-card">
          <div className="preview-box">Logo Preview</div>
          <div className="preview-list">
            <div></div>
            <div></div>
            <div></div>
          </div>
        </div>
      </section>

      <section className="service-grid">
        <a href="/detect" className="service-card">
          <h3>도용 탐지</h3>
          <p>이미지/텍스트 입력 후 유사 상표를 분석합니다.</p>
        </a>

        <a href="/generate" className="service-card">
          <h3>로고 생성</h3>
          <p>참고 데이터와 프롬프트를 기반으로 로고를 생성합니다.</p>
        </a>

        <a href="/trends" className="service-card">
          <h3>상표 트렌드</h3>
          <p>업종별 출원 흐름과 상표 데이터를 조회합니다.</p>
        </a>

        <a href="/mypage" className="service-card">
          <h3>마이페이지</h3>
          <p>저장한 이미지와 이용 기록을 확인합니다.</p>
        </a>
      </section>

      <Footer />
    </div>
  );
}

export default Home;
