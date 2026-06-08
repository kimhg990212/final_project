import { useMemo, useState } from "react";
import { detectPlagiarism } from "../api/plagiarism";
import "../css/detect.css";

function getRiskLevel(score) {
  if (score >= 80) return { label: "위험", colorClass: "risk-high" };
  if (score >= 50) return { label: "주의", colorClass: "risk-medium" };
  return { label: "안전", colorClass: "risk-low" };
}

function DetectPage({ googleToken }) {
  const [textQuery, setTextQuery] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [submittedText, setSubmittedText] = useState("");

  const canSubmit = Boolean(textQuery.trim() || imageFile);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] ?? null;
    setError("");
    setResult(null);
    setImageFile(file);

    if (file) {
      const reader = new FileReader();
      reader.onload = () => setImagePreview(reader.result);
      reader.readAsDataURL(file);
    } else {
      setImagePreview(null);
    }
  };

  const handleSubmit = async () => {
    if (!canSubmit) {
      setError("텍스트 또는 이미지를 입력해야 도용 탐지가 가능합니다.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setSubmittedText(textQuery.trim());

    try {
      const response = await detectPlagiarism({
        textQuery,
        imageFile,
        token: googleToken,
      });
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const summaryLabel = useMemo(() => {
    if (!result) return "";
    if (result.highest_similarity >= 80) return "위험: 매우 높은 유사도";
    if (result.highest_similarity >= 50) return "주의: 유사도가 확인되었습니다";
    return "안전: 유사 상표가 발견되지 않았습니다";
  }, [result]);

  const overallRisk = useMemo(() => {
    if (!result) return null;
    return getRiskLevel(result.highest_similarity);
  }, [result]);

  return (
    <main className="detect-page">
      <section className="detect-hero">
        <div>
          <span className="detect-badge">도용 탐지</span>
          <h1>텍스트·이미지 기반 상표 도용 의심 분석</h1>
          <p>
            AI 임베딩과 유사도 분석을 이용해 업로드한 로고 이미지와 텍스트
            설명을 기존 상표 데이터와 비교합니다.
          </p>
        </div>

        <div className="detect-hero-card">
          <div>
            <strong>검사 대상 입력</strong>
            <p>
              텍스트 또는 이미지를 업로드하면 도용 가능성을 자동 분석합니다.
            </p>
          </div>
        </div>
      </section>

      <section className="detect-grid">
        <div className="detect-panel">
          <div className="detect-card">
            <h2>도용 탐지 입력</h2>
            <label>상표명 또는 브랜드 설명</label>
            <textarea
              placeholder="예: 미니멀한 화이트톤 카페 로고, 글자 중심 심볼형"
              value={textQuery}
              onChange={(event) => {
                setTextQuery(event.target.value);
                setError("");
                setResult(null);
              }}
            />

            <label>로고 이미지 업로드</label>
            <div className="detect-file-input">
              <input
                type="file"
                accept="image/png, image/jpeg, image/jpg"
                onChange={handleFileChange}
              />
              <span>
                {imageFile
                  ? imageFile.name
                  : "PNG/JPG 이미지 파일을 선택하세요."}
              </span>
            </div>

            {imagePreview && (
              <div className="detect-preview">
                <img src={imagePreview} alt="선택한 이미지 미리보기" />
              </div>
            )}

            <div className="detect-tip">
              <strong>TIP</strong>
              <p>
                텍스트와 이미지를 동시에 입력하면 시각적 유사도와 텍스트 의미를
                모두 반영한 도용 탐지가 가능합니다.
              </p>
            </div>

            <button
              className="detect-submit"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? "분석 중..." : "도용 탐지 시작"}
            </button>

            {error && <p className="detect-error">{error}</p>}
          </div>
        </div>

        <div className="detect-result-panel">
          <div
            className={`detect-card detect-summary-card${overallRisk ? ` detect-summary--${overallRisk.colorClass}` : ""}`}
          >
            <h2>도용 분석 결과</h2>

            {!result ? (
              <div className="detect-empty">
                <p>입력 후 도용 탐지 버튼을 눌러 결과를 확인하세요.</p>
              </div>
            ) : (
              <>
                <div className="detect-summary-block">
                  <div>
                    <p className="detect-summary-label">총 매칭 항목</p>
                    <strong>{result.total_found}건</strong>
                  </div>
                  <div>
                    <p className="detect-summary-label">최고 유사도</p>
                    <strong
                      className={`detect-risk-value--${overallRisk.colorClass}`}
                    >
                      {result.highest_similarity}%
                    </strong>
                  </div>
                  <div>
                    <p className="detect-summary-label">위험 단계</p>
                    <strong
                      className={`detect-risk-value--${overallRisk.colorClass}`}
                    >
                      {overallRisk.label}
                    </strong>
                  </div>
                </div>

                <div className="detect-score-bar">
                  <div
                    className={`detect-score-fill detect-score-fill--${overallRisk.colorClass}`}
                    style={{
                      width: `${Math.min(result.highest_similarity, 100)}%`,
                    }}
                  />
                </div>

                <p className="detect-summary-text">
                  {result.result_summary_text}
                </p>
              </>
            )}
          </div>

          {result && result.results.length > 0 && (
            <div className="detect-card detect-list-card">
              <h3>상위 유사 상표</h3>
              <div className="detect-list">
                {result.results.map((item) => {
                  const risk = getRiskLevel(item.similarity_score);
                  return (
                    <article
                      key={item.trademark_id}
                      className={`detect-item detect-item--${risk.colorClass}`}
                    >
                      <div className="detect-item-header">
                        <span
                          className={`detect-item-risk-badge detect-item-risk-badge--${risk.colorClass}`}
                        >
                          {risk.label}
                        </span>
                        <h4>{item.trademark_name}</h4>
                        <span className="detect-item-score">
                          {item.similarity_score}%
                        </span>
                      </div>

                      <div className="detect-item-bar-wrap">
                        <div
                          className={`detect-item-bar-fill detect-item-bar-fill--${risk.colorClass}`}
                          style={{
                            width: `${Math.min(item.similarity_score, 100)}%`,
                          }}
                        />
                      </div>

                      {item.image_url && (
                        <div className="detect-item-preview">
                          <img
                            src={item.image_url}
                            alt={item.trademark_name}
                            onError={(e) => {
                              e.target.parentElement.style.display = "none";
                            }}
                          />
                        </div>
                      )}

                      <div className="detect-item-meta">
                        <span>
                          <b>출원번호</b> {item.application_number}
                        </span>
                        {item.applicant_name && (
                          <span>
                            <b>출원인</b> {item.applicant_name}
                          </span>
                        )}
                        {item.application_date && (
                          <span>
                            <b>출원일</b> {item.application_date}
                          </span>
                        )}
                      </div>

                      <p className="detect-item-explanation">
                        {item.explanation.summary}
                      </p>

                      <div className="detect-item-badges">
                        {item.explanation.image_contribution_pct > 0 && (
                          <span>
                            이미지 기여{" "}
                            {item.explanation.image_contribution_pct}%
                          </span>
                        )}
                        {submittedText && (
                          <span>
                            텍스트 기여 {item.explanation.text_contribution_pct}
                            %
                          </span>
                        )}
                        {item.explanation.keyword_matched?.length > 0 && (
                          <span>
                            키워드:{" "}
                            {item.explanation.keyword_matched.join(" · ")}
                          </span>
                        )}
                      </div>
                    </article>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

export default DetectPage;
