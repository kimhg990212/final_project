import { useEffect, useMemo, useState } from "react";
import { getGoogleMe } from "../api/auth";
import "../css/mypage.css";

const initialProfile = {
  nickname: "",
  email: "",
  joinedAt: "2026.03.18",
};

const activityHistory = [
  {
    id: 1,
    type: "search",
    title: "상표 검색",
    description: "Aurora 키워드로 유사 상표 24건을 확인했습니다.",
    time: "2026.06.02 09:40",
    downloadable: true,
  },
  {
    id: 2,
    type: "create",
    title: "로고 생성",
    description: "미니멀 스타일 시안 3개를 생성했습니다.",
    time: "2026.06.02 10:12",
    downloadable: true,
  },
  {
    id: 3,
    type: "download",
    title: "결과 다운로드",
    description: "최종 로고 결과물을 내려받았습니다.",
    time: "2026.06.02 10:21",
    downloadable: true,
  },
  {
    id: 4,
    type: "search",
    title: "상표 검색",
    description: "Nova 브랜드명으로 유사 사례를 다시 확인했습니다.",
    time: "2026.06.01 18:05",
    downloadable: true,
  },
  {
    id: 5,
    type: "create",
    title: "재생성 요청",
    description: "색상 조합을 바꿔 새로운 블루 계열 시안을 생성했습니다.",
    time: "2026.06.01 18:28",
    downloadable: true,
  },
  {
    id: 6,
    type: "download",
    title: "PNG 저장",
    description: "선택한 결과물을 PNG 파일로 저장했습니다.",
    time: "2026.06.01 19:02",
    downloadable: true,
  },
  {
    id: 7,
    type: "search",
    title: "상표 검색",
    description: "문구 조합 기준으로 추가 검색을 수행했습니다.",
    time: "2026.05.31 11:16",
    downloadable: true,
  },
  {
    id: 8,
    type: "create",
    title: "로고 생성",
    description: "텍스트 기반 로고 시안을 다시 생성했습니다.",
    time: "2026.05.31 11:42",
    downloadable: true,
  },
];

const tabLabels = [
  { key: "all", label: "전체" },
  { key: "search", label: "검색" },
  { key: "create", label: "생성" },
  { key: "download", label: "다운로드" },
];

const pageSize = 3;

function MyPage({ onDeleteAccount, googleToken }) {
  const [profile, setProfile] = useState(initialProfile);
  const [nickname, setNickname] = useState(initialProfile.nickname);
  const [email, setEmail] = useState(initialProfile.email);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [activeTab, setActiveTab] = useState("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [isDeleted, setIsDeleted] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const loadProfile = async () => {
      if (!googleToken) {
        return;
      }

      try {
        const user = await getGoogleMe({ token: googleToken });
        if (!isMounted) {
          return;
        }

        const nextProfile = {
          nickname: user.nickname || "",
          email: user.email || "",
          joinedAt: initialProfile.joinedAt,
        };

        setProfile(nextProfile);
        setNickname(nextProfile.nickname);
        setEmail(nextProfile.email);
      } catch (error) {
        if (isMounted) {
          setFeedbackMessage(
            error instanceof Error
              ? error.message
              : "API 요청에 실패하였습니다. 잠시후 시도해주세요.",
          );
        }
      }
    };

    loadProfile();

    return () => {
      isMounted = false;
    };
  }, [googleToken]);

  const filteredActivities = useMemo(() => {
    if (activeTab === "all") {
      return activityHistory;
    }

    return activityHistory.filter((activity) => activity.type === activeTab);
  }, [activeTab]);

  const totalPages = Math.max(1, Math.ceil(filteredActivities.length / pageSize));

  const currentItems = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    return filteredActivities.slice(startIndex, startIndex + pageSize);
  }, [currentPage, filteredActivities]);

  const stats = useMemo(() => {
    return activityHistory.reduce(
      (accumulator, activity) => {
        accumulator[activity.type] += 1;
        return accumulator;
      },
      { search: 0, create: 0, download: 0 },
    );
  }, []);

  const tabStats = {
    all: activityHistory.length,
    search: stats.search,
    create: stats.create,
    download: stats.download,
  };

  const handleTabChange = (tabKey) => {
    setActiveTab(tabKey);
    setCurrentPage(1);
  };

  const handleEditStart = () => {
    if (isDeleted) {
      return;
    }

    setIsEditingProfile(true);
    setFeedbackMessage("");
  };

  const handleEditCancel = () => {
    setNickname(profile.nickname);
    setEmail(profile.email);
    setIsEditingProfile(false);
    setFeedbackMessage("수정을 취소했습니다.");
  };

  const handleSave = () => {
    if (isDeleted) {
      setFeedbackMessage("탈퇴한 계정은 수정할 수 없습니다.");
      return;
    }

    setProfile((current) => ({
      ...current,
      nickname: nickname.trim() || current.nickname,
      email: email.trim() || current.email,
    }));

    setIsEditingProfile(false);
    setFeedbackMessage("개인정보가 저장되었습니다.");
  };

  const handleDownload = (activity) => {
    if (isDeleted) {
      setFeedbackMessage("탈퇴한 계정은 다운로드할 수 없습니다.");
      return;
    }

    const report = [
      `활동 유형: ${activity.type}`,
      `제목: ${activity.title}`,
      `설명: ${activity.description}`,
      `시간: ${activity.time}`,
    ].join("\n");

    const blob = new Blob([report], { type: "text/plain;charset=utf-8" });
    const downloadUrl = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = downloadUrl;
    anchor.download = `mypage-${activity.id}.txt`;
    anchor.click();
    URL.revokeObjectURL(downloadUrl);

    setFeedbackMessage(`${activity.title} 내역을 다운로드했습니다.`);
  };

  const handleDeleteConfirm = () => {
    setIsDeleted(true);
    setIsDeleteConfirmOpen(false);
    setFeedbackMessage("회원 탈퇴가 완료되었습니다.");
    onDeleteAccount();
  };

  return (
    <main className="mypage-main">
      <section className="mypage-shell">
        <div className="mypage-shell-header">
          <span className="page-kicker">Mypage</span>
          <h1>개인정보와 최근활동</h1>
        </div>

        <div className="mypage-grid">
          <section className="mypage-panel">
            <div className="panel-title">
              <span className="section-kicker">개인정보</span>
              <h2>내 정보</h2>
            </div>

            <div className="profile-rows">
              <label className="profile-row">
                <span>닉네임</span>
                <input
                  type="text"
                  value={nickname}
                  onChange={(event) => setNickname(event.target.value)}
                  disabled={isDeleted || !isEditingProfile}
                />
              </label>

              <label className="profile-row">
                <span>이메일</span>
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  disabled={isDeleted || !isEditingProfile}
                />
              </label>

              <div className="profile-meta">
                <div>
                  <span>가입일</span>
                  <strong>{profile.joinedAt}</strong>
                </div>
                <div>
                  <span>상태</span>
                  <strong>{isDeleted ? "탈퇴" : "활성"}</strong>
                </div>
              </div>
            </div>

            <div className="profile-actions">
              {!isEditingProfile ? (
                <button
                  type="button"
                  className="primary-action"
                  onClick={handleEditStart}
                  disabled={isDeleted}
                >
                  수정
                </button>
              ) : (
                <>
                  <button
                    type="button"
                    className="secondary-action"
                    onClick={handleEditCancel}
                    disabled={isDeleted}
                  >
                    수정 취소
                  </button>
                  <button
                    type="button"
                    className="primary-action"
                    onClick={handleSave}
                    disabled={isDeleted}
                  >
                    개인정보 저장
                  </button>
                </>
              )}
              <button
                type="button"
                className="danger-action"
                onClick={() => setIsDeleteConfirmOpen(true)}
                disabled={isDeleted}
              >
                회원 탈퇴
              </button>
            </div>

            {feedbackMessage ? <p className="feedback-message">{feedbackMessage}</p> : null}
          </section>

          <section className="mypage-panel">
            <div className="panel-title">
              <span className="section-kicker">최근활동</span>
              <h2>활동 내역</h2>
            </div>

            <div className="activity-tabs" role="tablist" aria-label="활동 유형 필터">
              {tabLabels.map((tab) => (
                <button
                  key={tab.key}
                  type="button"
                  className={activeTab === tab.key ? "activity-tab active" : "activity-tab"}
                  onClick={() => handleTabChange(tab.key)}
                >
                  {tab.label}
                  <span>{tabStats[tab.key]}</span>
                </button>
              ))}
            </div>

            <div className="activity-list">
              {currentItems.map((activity) => (
                <article key={activity.id} className="activity-item">
                  <div className={`activity-chip ${activity.type}`}>{activity.type}</div>

                  <div className="activity-content">
                    <div className="activity-topline">
                      <h3>{activity.title}</h3>
                      <span>{activity.time}</span>
                    </div>
                    <p>{activity.description}</p>
                  </div>

                  <button
                    type="button"
                    className="ghost-action"
                    onClick={() => handleDownload(activity)}
                    disabled={isDeleted || !activity.downloadable}
                  >
                    다운로드
                  </button>
                </article>
              ))}

              {currentItems.length === 0 ? (
                <div className="activity-empty">선택한 조건의 활동이 없습니다.</div>
              ) : null}
            </div>

            <div className="pagination-bar">
              <button
                type="button"
                className="pagination-button"
                onClick={() => setCurrentPage((current) => Math.max(1, current - 1))}
                disabled={currentPage === 1}
              >
                이전
              </button>

              <span className="pagination-indicator">
                {currentPage} / {totalPages}
              </span>

              <button
                type="button"
                className="pagination-button"
                onClick={() => setCurrentPage((current) => Math.min(totalPages, current + 1))}
                disabled={currentPage === totalPages}
              >
                다음
              </button>
            </div>
          </section>
        </div>
      </section>

      {isDeleteConfirmOpen ? (
        <div className="modal-backdrop" role="presentation">
          <div className="confirm-modal" role="dialog" aria-modal="true" aria-labelledby="delete-title">
            <h2 id="delete-title">회원 탈퇴를 진행할까요?</h2>
            <p>탈퇴를 확정하면 이 계정은 비활성 상태로 전환됩니다.</p>

            <div className="modal-actions">
              <button
                type="button"
                className="secondary-action"
                onClick={() => setIsDeleteConfirmOpen(false)}
              >
                취소
              </button>
              <button type="button" className="danger-action" onClick={handleDeleteConfirm}>
                탈퇴 확정
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );
}

export default MyPage;
