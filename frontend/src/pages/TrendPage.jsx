import { useEffect, useState } from "react";
import { getTrends } from "../api/trend";
import TrendCategorySelect from "../components/trend/TrendCategorySelect";
import TrendFilter from "../components/trend/TrendFilter";
import TrendSort from "../components/trend/TrendSort";
import TrendGrid from "../components/trend/TrendGrid";

function TrendPage() {
  const [classification, setClassification] = useState("");
  const [period, setPeriod] = useState("1y");
  const [sort, setSort] = useState("latest");
  const [items, setItems] = useState([]); // 누적 데이터
  const [page, setPage] = useState(1); // 현재 페이지
  const [total, setTotal] = useState(0); // 전체 건수
  const [loading, setLoading] = useState(true);

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

      {/* 카드 그리드 */}
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

            {/* 진행률 바 (선택) */}
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
    </div>
  );
}

export default TrendPage;
