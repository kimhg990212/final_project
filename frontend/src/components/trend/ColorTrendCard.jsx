import { getColorName } from "../../utils/colorName";

function ColorTrendCard({ colorData }) {
  if (!colorData || !colorData.colors || colorData.colors.length === 0) {
    return null;
  }

  return (
    <div className="mb-6 p-6 bg-purple-50 border border-purple-200 rounded-lg">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">
          🎨 색상 트렌드 분석
          <span className="text-sm font-normal text-gray-500 ml-2">
            (최근 3년 기준)
          </span>
        </h2>
        <span className="text-sm text-gray-500">
          ℹ️ K-means 클러스터링 (분석 {colorData.analyzed_count}개)
        </span>
      </div>
      {/*제외 색상 안내*/}
      <div className="mb-4 p-3 bg-red-50 border-l-4 border-red-400 rounded">
        <p className="text-sm text-red-800">
          <strong>⚠️ 분석 제외 색상 안내: </strong>이 분석에서는{" "}
          <strong>
            흰색(주로 배경), 검정(주로 텍스트), 회색(글자·도형 가장자리)
          </strong>
          을 제외했습니다. 이 세 가지 무채색은 상표 이미지의 70~90%를
          차지하지만, 실제 브랜드 컬러가 아니라 배경, 텍스트, 그리고 글자·도형
          주변에서 자연스럽게 생기는 가장자리 색상이기 때문에
          <strong> 브랜드 컬러 인사이트</strong>를 가리기 때문입니다. 추가로
          모든 카테고리에서 일관된 비율로 반복 등장하는{" "}
          <strong>비슷한 톤의 파란색들</strong>
          {"("}
          <strong style={{ color: "#8aafdb" }}>#8aafdb</strong>
          {", "}
          <strong style={{ color: "#7d99bb" }}>#7d99bb</strong>
          {", "}
          <strong style={{ color: "#7995b8" }}>#7995b8</strong>
          {" 등)"}도 함께 제외했습니다. 일반적으로 브랜드 컬러는 카테고리마다
          다양하게 분포되지만, 이 색상들은 카테고리와 무관하게 비슷한 비율로
          나타나는 점에서 KIPRIS 시스템의 이미지 처리 과정에서 들어가는 패턴으로
          추정되며, 실제 브랜드 컬러가 아니기 때문입니다.
        </p>
      </div>

      {/* 가로 배치 — 좌측 2 : 우측 1 */}
      <div className="flex flex-col md:flex-row gap-16">
        {/* 색상 빈도 시각화 -  CSS 막대 그래프 영역*/}
        {/* 좌측 CSS 막대 — flex-[2] => 가로 배치 — 좌측 2 : 우측 1 */}
        <div className="md:flex-[2] bg-gray-50 rounded p-3">
          <p className="text-sm text-gray-600 mb-3 font-semibold">
            색상 비율 시각화
          </p>
          <div className="space-y-3">
            {colorData.colors.map((c, idx) => (
              <div key={idx}>
                {/* 라벨 — 한글명만 */}
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-700 font-medium">
                    {getColorName(c.color)}
                  </span>
                  <span className="text-gray-700 font-medium">
                    {c.percentage}%
                  </span>
                </div>
                <div className="w-full bg-gray-100 border border-gray-400 rounded-full h-5 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${c.percentage}%`,
                      backgroundColor: c.color,
                      boxShadow: "inset 0 0 0 1px rgba(0, 0, 0, 0.35)",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/*색상 팔레트(우측) / 우측은 좌측의 1/2배 => 가로 배치 — 좌측 2 : 우측 1, 좌측과 높이가 안 맞아서 우측 콘텐츠를 위아래로 펴기 진행*/}
        <div className="md:flex-[1] flex flex-col">
          <p className="text-base font-semibold text-gray-700 mb-3">
            대표 색상
          </p>
          <div className="flex-1 flex flex-col justify-between">
            {colorData.colors.map((c, idx) => (
              <div key={idx} className="flex items-center gap-3 text-base">
                <div
                  className="w-10 h-10 rounded border border-gray-300 flex-shrink-0"
                  style={{ backgroundColor: c.color }}
                />
                {/*한글 색상명*/}
                <span className="text-gray-700 font-medium">
                  {getColorName(c.color)}
                </span>
                <span className="font-mono text-gray-500 text-sm">
                  {c.color}
                </span>
                <span className="text-gray-600">{c.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      {/*분석 메모*/}
      <div className="mt-4 p-4 bg-amber-50 border-l-4 border-amber-400 rounded">
        <p className="text-base text-gray-800">
          <strong>💡 분석 인사이트:</strong> 무채색과 시스템 공통 패턴 색상을
          제외한 후 도출된 실제 <strong>브랜드 컬러 분포</strong>입니다. 본
          분석은 전체 상표 (텍스트 + 도형)를 대상으로 한 통계적 경향성을
          보여주며, 카테고리별 색상 선호도를 신규 출원 시 디자인
          전략(차별화/안전성) 참고로 활용하실 수 있습니다.
        </p>
      </div>
    </div>
  );
}

export default ColorTrendCard;
