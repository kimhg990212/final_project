import { useEffect, useState } from "react";
import { getTrends, getTrendSummary, getTrendColors } from "../api/trend";

import TrendCategorySelect from "../components/trend/TrendCategorySelect";
import TrendFilter from "../components/trend/TrendFilter";
import TrendSort from "../components/trend/TrendSort";
import TrendGrid from "../components/trend/TrendGrid";
import ColorTrendCard from "../components/trend/ColorTrendCard";
import ClassificationStatsCard from "../components/trend/ClassificationStatsCard";
import { getTrendClassificationStats } from "../api/trend";

function TrendPage() {
  // useState 추가된 목록들
  const [classification, setClassification] = useState("");
  const [period, setPeriod] = useState("1y");
  const [sort, setSort] = useState("latest");
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);

  // 니스 코드 굵은 글씨 처리 위해 마크다운 ** → HTML <strong> 변환
  // LLM이 카테고리마다 3가지 다른 형식 사용
  const formatBold = (text) => {
    if (!text) return "";
    let result = text.replace(/\*\*([^*]+?)\*\*/g, "<strong>$1</strong>");
    result = result.replace(/'(\d{2}번\([^)]+\))'/g, "<strong>$1</strong>");
    result = result.replace(
      /(?<!<strong>)(\d{2}번\([^)]+\))(?!<\/strong>)/g,
      "<strong>$1</strong>",
    );

    return result;
  };
  const [colorData, setColorData] = useState(null);
  const [colorLoading, setColorLoading] = useState(false);
  const [statsData, setStatsData] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);

  // useEffect 추가된 목록들
  useEffect(() => {
    setLoading(true);
    getTrends({ classification, period, page, sort })
      .then((response) => {
        setItems((prev) =>
          page === 1 ? response.data : [...prev, ...response.data],
        );
        setTotal(response.total);
        setLoading(false);
      })
      .catch((error) => {
        console.error("API 호출 실패:", error);
        setLoading(false);
      });
  }, [classification, period, page, sort]);

  // LLM 요약
  useEffect(() => {
    if (!classification) {
      setSummary(null);
      return;
    }

    setSummaryLoading(true);
    getTrendSummary({ classification })
      .then((response) => {
        if (response) {
          // keywords 파싱 — 문자열이든 배열이든 OK
          let keywords = response.keywords;
          if (typeof keywords === "string") {
            try {
              keywords = JSON.parse(keywords);
            } catch (e) {
              keywords = [];
            }
          }
          if (!Array.isArray(keywords)) {
            keywords = [];
          }

          setSummary({
            ...response,
            keywords,
          });
        } else {
          setSummary(null);
        }
      })
      .catch((err) => {
        console.error("요약 호출 실패:", err);
        setSummary(null);
      })
      .finally(() => setSummaryLoading(false));
  }, [classification]); // 카테고리 단위별 요약

  // K-means 색상 분석 시각화
  useEffect(() => {
    if (!classification) {
      setColorData(null);
      return;
    }

    setColorLoading(true);
    getTrendColors({ classification })
      .then((response) => setColorData(response))
      .catch((err) => {
        console.error("색상 호출 실패:", err);
        setColorData(null);
      })
      .finally(() => setColorLoading(false));
  }, [classification]);

  // 카테고리 그룹 내 니스 코드별 출원 빈도 조회 시각화
  useEffect(() => {
    if (!classification) {
      setStatsData(null);
      return;
    }
    setStatsLoading(true);
    getTrendClassificationStats({ classification })
      .then((response) => setStatsData(response))
      .catch((err) => {
        console.error("분류 빈도 호출 실패:", err);
        setStatsData(null);
      })
      .finally(() => setStatsLoading(false));
  }, [classification]);

  // 필터 변경 시 page 1로 리셋
  const handleClassificationChange = (newClassification) => {
    setPage(1);
    setClassification(newClassification);
  };

  const handlePeriodChange = (newPeriod) => {
    setPage(1);
    setPeriod(newPeriod);
  };

  // 정렬
  const handleSortChange = (newSort) => {
    setPage(1);
    setSort(newSort);
  };

  // 더보기 버튼
  const handleLoadMore = () => {
    setPage(page + 1);
  };

  const hasMore = items.length < total;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">업종별 트렌드</h1>
      <p className="text-sm text-gray-500 mb-6">총 {total}개 결과</p>

      {/* 필터 영역 */}
      <div className="flex flex-wrap items-end gap-6 mb-6">
        <TrendCategorySelect
          classification={classification}
          onClassificationChange={handleClassificationChange}
        />
        <TrendFilter period={period} onPeriodChange={handlePeriodChange} />
        <TrendSort sort={sort} onSortChange={handleSortChange} />
      </div>

      {/* 그리드 빠른 이동 버튼 */}
      <div className="flex justify-start mb-6">
        <a
          href="#trademark-grid"
          className="inline-flex items-center gap-2 px-4 py-2 bg-purple-50 border-2 border-purple-700 text-purple-700 font-semibold rounded-lg hover:bg-purple-100 transition shadow-md hover:shadow-lg"
        >
          <span className="text-xs bg-purple-700 text-white px-2 py-0.5 rounded">
            CLICK
          </span>
          상표 목록 {total.toLocaleString()}건 바로 가기
          <span className="text-lg">↓</span>
        </a>
      </div>

      {/* 화면에 출력할 LLM 요약 카드 */}
      {summaryLoading ? (
        <div className="mb-6 p-6 bg-gray-50 rounded-lg text-center text-gray-500">
          AI 분석 데이터 로딩 중...
        </div>
      ) : summary ? (
        <div className="mb-6 p-6 bg-purple-50 border border-purple-200 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">📊 AI 트렌드 요약</h2>
            <span className="text-sm text-gray-500">
              ℹ️ 카테고리 그룹 기준 분석 — 세부 코드별 트렌드는 일반화될 수 있음
            </span>
          </div>
          {/* summary_text 굵은 글씨 표현 위해 HTML 직접 렌더링 / 브라우저가 직접 HTML 해석 / 별표가 HTML로 변환되어 안 보이게 됨*/}
          <div
            className="text-gray-800 leading-relaxed mb-3"
            dangerouslySetInnerHTML={{
              __html: formatBold(summary.summary_text),
            }}
          />
          {summary.keywords && summary.keywords.length > 0 && (
            <div className="mt-3">
              <p className="text-sm font-semibold text-gray-700 mb-2">
                주요 키워드
              </p>
              <div className="flex flex-wrap gap-2">
                {summary.keywords.map((kw, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-full"
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}
          <div className="mt-4 text-xs text-gray-500 border-t border-purple-200 pt-3 space-y-1">
            <div>
              분석 기간: {summary.period_start} ~ {summary.period_end} · 분석일:{" "}
              {summary.generated_at?.split("T")[0]}
            </div>
            <div>
              분석 모델: {summary.model_name} (LG AI Research) · 데이터: KIPRIS
              Plus API
            </div>
          </div>
        </div>
      ) : (
        <div className="mb-6 p-8 bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-purple-200 rounded-lg">
          <div className="text-center">
            {/* 안내 화살표 */}
            <div className="mb-8 text-gray-400 animate-bounce">
              ↑ 페이지 상단에서 업종 선택
            </div>

            {/* 큰 아이콘 */}
            <div className="text-6xl mb-4">📊</div>

            {/* 메인 메시지 */}
            <h3 className="text-xl font-bold text-gray-800 mb-3">
              업종을 선택하면 AI 분석 결과를 확인하실 수 있습니다.
            </h3>

            {/* 부가 설명 */}
            <p className="text-base text-gray-600 mb-6 max-w-2xl mx-auto">
              카테고리별 트렌드 요약 · 색상 분포 · 업종 빈도를 한눈에 확인하실
              수 있습니다.
            </p>

            {/* 미리 보기 */}
            <div className="flex flex-wrap justify-center gap-3 text-sm">
              <span className="px-4 py-2 bg-white border border-purple-200 rounded-full text-purple-700">
                📝 AI 트렌드 요약
              </span>
              <span className="px-4 py-2 bg-white border border-indigo-200 rounded-full text-indigo-700">
                🎨 색상 트렌드 분석
              </span>
              <span className="px-4 py-2 bg-white border border-violet-200 rounded-full text-violet-700">
                📊 업종 코드별 출원 빈도
              </span>
            </div>
          </div>
        </div>
      )}

      {/* K-means 색상 분석 결과를 CSS 막대 그래프로 시각화 (상위 5개) */}
      {classification && colorData && !colorLoading && (
        <ColorTrendCard colorData={colorData} />
      )}

      {/* 분류 코드별 출원 빈도 시각화 (니스 코드 기반) */}
      {classification && statsData && !statsLoading && (
        <ClassificationStatsCard statsData={statsData} />
      )}

      {/* 카드 그리드 */}
      {/* 빠른 이동 위해 ID 생성 - 버튼 타겟) */}
      <div id="trademark-grid">
        {loading && page === 1 ? (
          <p className="text-center py-10">로딩 중...</p>
        ) : items.length === 0 ? (
          <p className="text-center py-10 text-gray-500">데이터가 없습니다.</p>
        ) : (
          <>
            <TrendGrid items={items} />

            <div className="text-center mt-6 space-y-3">
              <p className="text-sm text-gray-500">
                전체 {total}개 중 {items.length}개 표시
              </p>

              {/* 진행률 바 */}
              <div className="max-w-xs mx-auto h-1 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 transition-all"
                  style={{ width: `${(items.length / total) * 100}%` }}
                />
              </div>

              {/* 더보기 버튼 */}
              {hasMore ? (
                <button
                  onClick={handleLoadMore}
                  disabled={loading}
                  className="h-10 px-6 rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition"
                >
                  {loading
                    ? "불러오는 중..."
                    : `더보기 (${total - items.length}개 더)`}
                </button>
              ) : (
                <p className="text-sm text-gray-500">
                  모든 결과를 확인하셨습니다
                </p>
              )}
            </div>
          </>
        )}
        {/* 출처 안내 - 모든 상태에서 표시 */}
        <div className="mt-12 pt-6 border-t border-gray-200 text-sm text-gray-500 space-y-2 max-w-3xl mx-auto">
          <p className="font-semibold text-gray-700 mb-2">
            📋 데이터 출처 안내
          </p>
          <p>
            · 본 서비스는{" "}
            <strong>KIPRIS(특허청 특허정보검색서비스) Plus Open API</strong>를
            통해 수집한 공개 상표 데이터를 기반으로 합니다.
          </p>
          <p>
            · 본 트렌드 페이지는 <strong>업종별 상표 출원 조회 기능</strong>과{" "}
            <strong>AI 트렌드 요약</strong>을 결합하여, 사용자가{" "}
            <strong>디자인·브랜딩 트렌드를 직관적으로 파악</strong>할 수 있도록
            구성되었습니다.
          </p>

          <p>
            · AI 트렌드 요약은 <strong>EXAONE-3.5-2.4B (LG AI Research)</strong>{" "}
            모델로 생성된 AI 분석 결과로, 참고용으로만 활용 바랍니다.
          </p>
          <p>· KIPRIS Plus API 활용 약관을 준수합니다.</p>
          <p>
            · 원본 상표 정보는{" "}
            <a
              href="https://www.kipris.or.kr"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              KIPRIS 공식 사이트
            </a>
            에서 확인하실 수 있습니다.
          </p>
        </div>
      </div>
    </div>
  );
}

export default TrendPage;
