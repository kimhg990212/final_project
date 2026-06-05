function ProfileForm({
  formState,
  onChange,
  onSubmit,
  onReset,
  feedbackMessage,
  disabled = false,
}) {
  return (
    <section className="mypage-card form-card">
      <div className="section-heading">
        <span className="section-kicker">정보 수정</span>
        <h2>개인정보 수정</h2>
      </div>

      <form className="profile-form" onSubmit={onSubmit}>
        <label>
          닉네임
          <input
            type="text"
            name="nickname"
            value={formState.nickname}
            onChange={onChange}
            disabled={disabled}
            placeholder="닉네임을 입력하세요"
          />
        </label>

        <label>
          이메일
          <input
            type="email"
            name="email"
            value={formState.email}
            onChange={onChange}
            disabled={disabled}
            placeholder="이메일을 입력하세요"
          />
        </label>

        <label>
          현재 비밀번호
          <input
            type="password"
            name="currentPassword"
            value={formState.currentPassword}
            onChange={onChange}
            disabled={disabled}
            placeholder="현재 비밀번호"
          />
        </label>

        <label>
          새 비밀번호
          <input
            type="password"
            name="newPassword"
            value={formState.newPassword}
            onChange={onChange}
            disabled={disabled}
            placeholder="새 비밀번호"
          />
        </label>

        <label>
          새 비밀번호 확인
          <input
            type="password"
            name="confirmPassword"
            value={formState.confirmPassword}
            onChange={onChange}
            disabled={disabled}
            placeholder="비밀번호를 다시 입력하세요"
          />
        </label>

        {feedbackMessage ? <p className="feedback-message">{feedbackMessage}</p> : null}

        <div className="form-actions">
          <button
            type="button"
            className="secondary-action"
            onClick={onReset}
            disabled={disabled}
          >
            변경 취소
          </button>
          <button type="submit" className="primary-action" disabled={disabled}>
            저장하기
          </button>
        </div>
      </form>
    </section>
  );
}

export default ProfileForm;
