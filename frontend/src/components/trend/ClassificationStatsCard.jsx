import { NICE_CODES } from "../../constants/niceCodes";

// 니스 코드 → 한글 라벨 변환 함수
function getNiceCodeLabel(code) {
  const found = NICE_CODES.find((nc) => nc.code === code);
  return found ? found.label : "";
}
function ClassificationStatsCard({ statsData }) {
  // 백엔드 응답 구조에 맞춤(디버깅 코드로 statsData의 타입 콘솔창에서 확인 시 백엔드가 객체로 감싸서 응답하고 있으므로)
  // ㄴ data 필드 안에 배열" 구조라 객체 타입으로 응답함
  if (!statsData || !statsData.data || statsData.data.length === 0) {
    return null;
  }
  const items = statsData.data;
  const category = statsData.category;
  const total = statsData.total;

  // 최대값 (가장 큰 막대 기준으로 비율 계산)
  const maxCount = Math.max(...items.map((s) => s.count));

  return (
    <div className="mb-6 p-6 bg-purple-50 border border-purple-200 rounded-lg">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">
          📊 업종 코드별 출원 빈도
          <span className="text-sm font-normal text-gray-500 ml-2">
            ({category} — 최근 3년 기준)
          </span>
        </h2>
        <span className="text-sm text-gray-500">
          ℹ️ 카테고리 그룹 내 니스 코드별 출원 수(총 {total.toLocaleString()}건)
        </span>
      </div>

      <div className="space-y-3">
        {/*data 추출한 items 사용*/}
        {items.map((s, idx) => (
          <div key={idx}>
            {/* 라벨 — 코드 + 한글 + 건수 */}
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-700 font-medium">
                {s.code}번
                <span className="text-gray-500 font-normal ml-2">
                  ({getNiceCodeLabel(s.code)})
                </span>
              </span>
              <span className="text-gray-700">
                {s.count.toLocaleString()}건
              </span>
            </div>
            {/* 막대 */}
            <div className="w-full bg-gray-100 border border-gray-400 rounded-full h-5 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-purple-400 to-purple-600 transition-all"
                style={{ width: `${(s.count / maxCount) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ClassificationStatsCard;
