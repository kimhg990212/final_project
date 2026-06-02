function ProfileSummary({ profile, stats }) {
  return (
    <section className="mypage-card summary-card">
      <div className="section-heading">
        <span className="section-kicker">개인정보</span>
        <h2>내 계정 요약</h2>
      </div>

      <div className="summary-grid">
        <article className="summary-item">
          <span className="summary-label">닉네임</span>
          <strong>{profile.nickname}</strong>
        </article>

        <article className="summary-item">
          <span className="summary-label">이메일</span>
          <strong>{profile.email}</strong>
        </article>

        <article className="summary-item">
          <span className="summary-label">가입일</span>
          <strong>{profile.joinedAt}</strong>
        </article>

        <article className="summary-item">
          <span className="summary-label">활동 상태</span>
          <strong>{profile.status}</strong>
        </article>
      </div>

      <div className="summary-stats">
        <div>
          <span>검색</span>
          <strong>{stats.search}</strong>
        </div>
        <div>
          <span>생성</span>
          <strong>{stats.create}</strong>
        </div>
        <div>
          <span>다운로드</span>
          <strong>{stats.download}</strong>
        </div>
      </div>
    </section>
  );
}

export default ProfileSummary;
