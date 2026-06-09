import { useEffect, useMemo, useState } from "react";

import { getGoogleMe, updateGoogleMe } from "../api/auth";
import { getMyPageActivities } from "../api/mypage";
import "../css/mypage.css";

const BASE_URL = "http://localhost:5000";

const initialProfile = {
  nickname: "",
  email: "",
  joinedAt: "2026.03.18",
};

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

function getActivityTitle(activity) {
  if (activity.type === "search") {
    return getSearchTitle(activity);
  }

  return activity.title || activityTypeLabels[activity.type] || "활동";
}

function getActivityDescription(activity) {
  if (activity.type === "search") {
    return getSearchDescription(activity);
  }

  return activity.description || "상세 설명이 없습니다.";
}

function getImageDownloadUrl(imagePath) {
  if (!imagePath) return "";
  if (/^https?:\/\//i.test(imagePath)) return imagePath;

  const normalizedPath = imagePath.startsWith("/")
    ? imagePath.slice(1)
    : imagePath;

  return `${BASE_URL}/${normalizedPath}`;
}

function getFileNameFromPath(imagePath, fallbackName) {
  if (!imagePath) return fallbackName;

  const cleanPath = imagePath.split("?")[0];
  const lastSegment = cleanPath.split("/").pop();

  if (!lastSegment) return fallbackName;

  return lastSegment.includes(".") ? lastSegment : fallbackName;
}

function MyPage({ onDeleteAccount, googleToken, onProfileUpdate }) {
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
  const [activities, setActivities] = useState([]);
  const [isLoadingActivities, setIsLoadingActivities] = useState(false);

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

    const loadActivities = async () => {
      if (!googleToken) {
        setActivities([]);
        setIsLoadingActivities(false);
        return;
      }

      setIsLoadingActivities(true);
      try {
        const items = await getMyPageActivities({ token: googleToken });
        if (!isMounted) return;
        setActivities(Array.isArray(items) ? items : []);
      } catch (error) {
        if (isMounted) {
          setFeedbackMessage(error instanceof Error ? error.message : "활동 내역을 불러오지 못했습니다.");
        }
      } finally {
        if (isMounted) {
          setIsLoadingActivities(false);
        }
      }
    };

    loadActivities();
    return () => {
      isMounted = false;
    };
  }, [googleToken]);

  const filteredActivities = useMemo(() => {
    if (activeTab === "all") return activities;
    return activities.filter((activity) => activity.type === activeTab);
  }, [activeTab, activities]);

  const totalPages = Math.max(1, Math.ceil(filteredActivities.length / pageSize));
  const safeCurrentPage = Math.min(currentPage, totalPages);

  const currentItems = useMemo(() => {
    const startIndex = (safeCurrentPage - 1) * pageSize;
    return filteredActivities.slice(startIndex, startIndex + pageSize);
  }, [filteredActivities, safeCurrentPage]);

  const stats = useMemo(() => {
    return {
      search: activities.filter((activity) => activity.type === "search").length,
      create: activities.filter((activity) => activity.type === "create").length,
      download: activities.filter((activity) => activity.type === "download").length,
    };
  }, [activities]);

  const tabStats = {
    all: activities.length,
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
      onProfileUpdate?.(nextProfile.nickname);
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

    if (activity.type === "create" || activity.type === "download") {
      const imageUrl = getImageDownloadUrl(activity.image_path || activity.image_url);

      if (!imageUrl) {
        setFeedbackMessage("다운로드할 이미지 경로가 없습니다.");
        return;
      }

      fetch(imageUrl)
        .then((response) => {
          if (!response.ok) {
            throw new Error("이미지 다운로드에 실패했습니다.");
          }

          return response.blob();
        })
        .then((blob) => {
          const downloadUrl = URL.createObjectURL(blob);
          const anchor = document.createElement("a");
          anchor.href = downloadUrl;
          anchor.download = getFileNameFromPath(
            activity.image_path || activity.image_url,
            `mypage-${activity.id}.png`,
          );
          anchor.click();
          URL.revokeObjectURL(downloadUrl);

          setFeedbackMessage(`${getActivityTitle(activity)} 이미지 다운로드가 완료되었습니다.`);
        })
        .catch((error) => {
          setFeedbackMessage(
            error instanceof Error ? error.message : "이미지 다운로드에 실패했습니다.",
          );
        });

      return;
    }

    const resultRows = Array.isArray(activity.results) ? activity.results : [];
    const reportHeader = [
      `유형: ${activity.type}`,
      `제목: ${getActivityTitle(activity)}`,
      `설명: ${getActivityDescription(activity)}`,
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
                  `- 상태: ${result.application_status || ""}`,
                  `- 이미지 URL: ${result.image_url || ""}`,
                  `- 유사도: ${result.similarity_score ?? ""}`,
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

    setFeedbackMessage(`${getActivityTitle(activity)} 내역의 다운로드가 완료되었습니다.`);
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

            {isLoadingActivities ? (
              <div className="activity-empty">활동 내역을 불러오는 중입니다.</div>
            ) : (
              <div className="activity-list">
                {currentItems.map((activity) => (
                  <article key={activity.id} className="activity-item">
                    <div className={`activity-chip ${activity.type}`}>
                      {activityTypeLabels[activity.type] || activity.type}
                    </div>

                    <div className="activity-content">
                      <div className="activity-topline">
                        <h3>{getActivityTitle(activity)}</h3>
                        <span>{activity.time}</span>
                      </div>
                      <p>{getActivityDescription(activity)}</p>
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
                disabled={safeCurrentPage === 1}
              >
                이전
              </button>

              <span className="pagination-indicator">
                {safeCurrentPage} / {totalPages}
              </span>

              <button
                type="button"
                className="pagination-button"
                onClick={() => setCurrentPage((current) => Math.min(totalPages, current + 1))}
                disabled={safeCurrentPage === totalPages}
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
