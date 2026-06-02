function AccountActions({ onDeleteAccount, accountStatus }) {
  const isDisabled = accountStatus === "탈퇴 처리 완료";

  return (
    <section className="mypage-card danger-card">
      <div className="section-heading">
        <span className="section-kicker">계정 관리</span>
        <h2>회원 탈퇴</h2>
      </div>

      <p className="danger-copy">
        탈퇴하면 저장된 개인정보와 활동 이력은 더 이상 표시되지 않도록 처리됩니다.
        실제 서버 연동 시에는 비활성화 상태와 데이터 보관 정책을 분리하는 것이 좋습니다.
      </p>

      <div className="danger-status">
        <span>계정 상태</span>
        <strong>{accountStatus}</strong>
      </div>

      <button
        type="button"
        className="danger-action"
        onClick={onDeleteAccount}
        disabled={isDisabled}
      >
        {isDisabled ? "탈퇴 완료" : "회원 탈퇴"}
      </button>
    </section>
  );
}

export default AccountActions;
