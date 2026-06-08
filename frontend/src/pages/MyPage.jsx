import { useEffect, useMemo, useState } from "react";

import { getGoogleMe, updateGoogleMe } from "../api/auth";
import { getSearchHistory } from "../api/mypage";
import "../css/mypage.css";

const initialProfile = {
  nickname: "",
  email: "",
  joinedAt: "2026.03.18",
};

const staticActivities = [
  {
    id: 1001,
    type: "create",
    title: "로고 생성",
    description: "최근 생성한 로고 3건을 확인했습니다.",
    time: "2026.06.02 10:12",
    downloadable: true,
  },
  {
    id: 1002,
    type: "download",
    title: "결과 다운로드",
    description: "최종 로고 결과물을 내려받았습니다.",
    time: "2026.06.02 10:21",
    downloadable: true,
  },
  {
    id: 1003,
    type: "create",
    title: "아이디어 생성",
    description: "새로운 브랜드 컨셉을 생성했습니다.",
    time: "2026.06.01 18:28",
    downloadable: true,
  },
  {
    id: 1004,
    type: "download",
    title: "PNG 저장",
    description: "선택한 결과물을 PNG 파일로 저장했습니다.",
    time: "2026.06.01 19:02",
    downloadable: true,
  },
];

const tabLabels = [
  { key: "all", label: "전체" },
  { key: "search", label: "검색" },
  { key: "create", label: "생성" },
  { key: "download", label: "다운로드" },
];

const activityTypeLabels = {
  search: "검색",
  create: "생성",
  download: "다운로드",
};

const pageSize = 3;

function getSearchTitle() {
  return "유사 검색";
}

function getSearchDescription(activity) {
  const parts = [];

  if (activity.input_text) {
    parts.push(activity.input_text);
  }

  if (activity.highest_similarity !== undefined) {
    parts.push(`최고 유사도 ${activity.highest_similarity}%`);
  }

  if (activity.total_found !== undefined) {
    parts.push(`결과 ${activity.total_found}건`);
  }

  return parts.join(" | ") || "상세 설명이 없습니다.";
}

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
  const [isSaving, setIsSaving] = useState(false);
  const [searchActivities, setSearchActivities] = useState([]);
  const [isLoadingSearchActivities, setIsLoadingSearchActivities] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const loadProfile = async () => {
      if (!googleToken) return;

      try {
        const user = await getGoogleMe({ token: googleToken });
        if (!isMounted) return;

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
          setFeedbackMessage(error instanceof Error ? error.message : "프로필 정보를 불러오지 못했습니다.");
        }
      }
    };

    loadProfile();
    return () => {
      isMounted = false;
    };
  }, [googleToken]);

  useEffect(() => {
    let isMounted = true;

    const loadSearchActivities = async () => {
      setIsLoadingSearchActivities(true);
      try {
        const items = await getSearchHistory();
        if (!isMounted) return;
        setSearchActivities(items || []);
      } catch (error) {
        if (isMounted) {
          setFeedbackMessage(error instanceof Error ? error.message : "검색 내역을 불러오지 못했습니다.");
        }
      } finally {
        if (isMounted) {
          setIsLoadingSearchActivities(false);
        }
      }
    };

    loadSearchActivities();
    return () => {
      isMounted = false;
    };
  }, []);

  const allActivities = useMemo(() => {
    return [...searchActivities, ...staticActivities].sort((left, right) => right.time.localeCompare(left.time));
  }, [searchActivities]);

  const filteredActivities = useMemo(() => {
    if (activeTab === "all") return allActivities;
    if (activeTab === "search") return searchActivities;
    return staticActivities.filter((activity) => activity.type === activeTab);
  }, [activeTab, allActivities, searchActivities]);

  const totalPages = Math.max(1, Math.ceil(filteredActivities.length / pageSize));

  const currentItems = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    return filteredActivities.slice(startIndex, startIndex + pageSize);
  }, [currentPage, filteredActivities]);

  const stats = useMemo(() => {
    return {
      search: searchActivities.length,
      create: staticActivities.filter((activity) => activity.type === "create").length,
      download: staticActivities.filter((activity) => activity.type === "download").length,
    };
  }, [searchActivities]);

  const tabStats = {
    all: allActivities.length,
    search: stats.search,
    create: stats.create,
    download: stats.download,
  };

  const handleTabChange = (tabKey) => {
    setActiveTab(tabKey);
    setCurrentPage(1);
  };

  const handleEditStart = () => {
    if (isDeleted || isSaving) return;
    setIsEditingProfile(true);
    setFeedbackMessage("");
  };

  const handleEditCancel = () => {
    setNickname(profile.nickname);
    setEmail(profile.email);
    setIsEditingProfile(false);
    setFeedbackMessage("수정을 취소했습니다.");
  };

  const handleSave = async () => {
    if (isDeleted || isSaving) return;

    if (!googleToken) {
      setFeedbackMessage("로그인 정보가 없어 저장할 수 없습니다.");
      return;
    }

    const nextNickname = nickname.trim();
    const nextEmail = email.trim();

    if (!nextNickname || !nextEmail) {
      setFeedbackMessage("닉네임과 이메일을 모두 입력해주세요.");
      return;
    }

    setIsSaving(true);
    try {
      const result = await updateGoogleMe({
        token: googleToken,
        email: nextEmail,
        nickname: nextNickname,
      });

      const nextProfile = {
        nickname: result.nickname || "",
        email: result.email || "",
        joinedAt: profile.joinedAt,
      };

      setProfile(nextProfile);
      setNickname(nextProfile.nickname);
      setEmail(nextProfile.email);
      setIsEditingProfile(false);
      setFeedbackMessage("개인정보가 저장되었습니다.");
    } catch (error) {
      setFeedbackMessage(error instanceof Error ? error.message : "프로필 저장에 실패했습니다.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDownload = (activity) => {
    if (isDeleted) {
      setFeedbackMessage("탈퇴한 계정은 다운로드할 수 없습니다.");
      return;
    }

    const resultRows = Array.isArray(activity.results) ? activity.results : [];
    const reportHeader = [
      `유형: ${activity.type}`,
      `제목: ${activity.type === "search" ? "유사 검색" : activity.title}`,
      `설명: ${activity.type === "search" ? getSearchDescription(activity) : activity.description}`,
      `시간: ${activity.time}`,
      activity.history_id ? `기록 ID: ${activity.history_id}` : null,
      activity.highest_similarity !== undefined ? `최고 유사도: ${activity.highest_similarity}%` : null,
      activity.total_found !== undefined ? `결과 수: ${activity.total_found}` : null,
      "",
    ]
      .filter((line) => line !== null)
      .join("\n");

    const reportBody =
      resultRows.length > 0
        ? resultRows
            .map(
              (result, index) =>
                [
                  `결과 ${index + 1}`,
                  `- 상표명: ${result.title || ""}`,
                  `- 출원인: ${result.applicant_name || ""}`,
                  `- 출원일: ${result.application_date || ""}`,
                  `- 심사상태: ${result.application_status || ""}`,
                  `- 이미지 URL: ${result.image_url || ""}`,
                  `- 유사도 점수: ${result.similarity_score ?? ""}`,
                  `- 텍스트 점수: ${result.text_score ?? ""}`,
                  `- 이미지 점수: ${result.image_score ?? ""}`,
                ].join("\n"),
            )
            .join("\n\n")
        : "상세 결과가 없습니다.";

    const report = `${reportHeader}${reportBody}`;
    const blob = new Blob([report], { type: "text/plain;charset=utf-8" });
    const downloadUrl = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = downloadUrl;
    anchor.download = `mypage-${activity.id}.txt`;
    anchor.click();
    URL.revokeObjectURL(downloadUrl);

    setFeedbackMessage(`${activity.type === "search" ? "유사 검색" : activity.title} 이력의 다운로드가 완료되었습니다.`);
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
          <h1>개인정보와 최근 활동</h1>
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
                  disabled={isDeleted || !isEditingProfile || isSaving}
                />
              </label>

              <label className="profile-row">
                <span>이메일</span>
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  disabled={isDeleted || !isEditingProfile || isSaving}
                />
              </label>

              <div className="profile-meta">
                <div>
                  <span>가입일</span>
                  <strong>{profile.joinedAt}</strong>
                </div>
                <div>
                  <span>상태</span>
                  <strong>{isDeleted ? "탈퇴" : "정상"}</strong>
                </div>
              </div>
            </div>

            <div className="profile-actions">
              {!isEditingProfile ? (
                <button
                  type="button"
                  className="primary-action"
                  onClick={handleEditStart}
                  disabled={isDeleted || isSaving}
                >
                  수정
                </button>
              ) : (
                <>
                  <button
                    type="button"
                    className="secondary-action"
                    onClick={handleEditCancel}
                    disabled={isDeleted || isSaving}
                  >
                    수정 취소
                  </button>
                  <button
                    type="button"
                    className="primary-action"
                    onClick={handleSave}
                    disabled={isDeleted || isSaving}
                  >
                    개인정보 저장
                  </button>
                </>
              )}
              <button
                type="button"
                className="danger-action"
                onClick={() => setIsDeleteConfirmOpen(true)}
                disabled={isDeleted || isSaving}
              >
                회원 탈퇴
              </button>
            </div>

            {feedbackMessage ? <p className="feedback-message">{feedbackMessage}</p> : null}
          </section>

          <section className="mypage-panel">
            <div className="panel-title">
              <span className="section-kicker">최근 활동</span>
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

            {activeTab === "search" && isLoadingSearchActivities ? (
              <div className="activity-empty">검색 내역을 불러오는 중입니다.</div>
            ) : (
              <div className="activity-list">
                {currentItems.map((activity) => (
                  <article key={activity.id} className="activity-item">
                    <div className={`activity-chip ${activity.type}`}>
                      {activityTypeLabels[activity.type] || activity.type}
                    </div>

                    <div className="activity-content">
                      <div className="activity-topline">
                        <h3>{activity.type === "search" ? getSearchTitle(activity) : activity.title}</h3>
                        <span>{activity.time}</span>
                      </div>
                      <p>{activity.type === "search" ? getSearchDescription(activity) : activity.description}</p>
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
                  <div className="activity-empty">표시할 활동 내역이 없습니다.</div>
                ) : null}
              </div>
            )}

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
            <p>탈퇴를 선택하면 계정은 비활성 상태로 전환됩니다.</p>

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
