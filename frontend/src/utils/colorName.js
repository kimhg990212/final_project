// 색상 트렌드 분석에서 색상을 한글로 표기
export function getColorName(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);

  // 흰색 / 검정 / 회색 판정 (R≈G≈B)
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const isGray = max - min < 15; // RGB 차이 작으면 회색계열

  // 무채색
  if (isGray) {
    if (max > 240) return "흰색";
    if (max > 200) return "밝은 회색";
    if (max > 100) return "회색";
    if (max > 40) return "진한 회색";
    return "검정";
  }

  // 정밀한 컬러 판정
  // 크림 계열 (R, G 매우 높음 + B 중간)
  if (r > 240 && g > 220 && b < 200 && r > g && g > b) {
    return "연한 노랑 계열";
  }
  // 베이지/탄/갈색 계열 (R > G > B, 모두 높은 톤)
  if (r > 180 && g > 150 && b > 130 && r > g && g > b) {
    return "베이지 계열";
  }

  // 갈색 계열 (R > G > B, 중간 톤)
  if (r > 100 && r < 200 && g > 80 && g < 180 && b < 130 && r > g && g > b) {
    return "갈색 계열";
  }

  // 진한 빨강/마룬 (R 우세, 매우 낮은 G, B)
  if (r > 100 && r < 180 && g < 60 && b < 80) {
    return "진한 빨강 계열";
  }

  // 빨강 계열 (R 우세, 낮은 G, B)
  if (r > 180 && g < 100 && b < 100) return "빨강 계열";

  // 주황 계열: R 우세 + G 중간 + B 낮음
  if (r > 200 && g > 100 && g < 200 && b < 100) return "주황 계열";

  // 살구/연주황 계열 (주황보다 B가 살짝 높음)
  if (r > 200 && g > 130 && g < 200 && b > 100 && b < g) {
    return "살구 계열";
  }

  // 노랑 계열: R, G 모두 높음 + B 낮음
  if (r > 200 && g > 200 && b < 150) return "노랑 계열";

  // 초록 계열: G 우세
  if (g > r && g > b) return "초록 계열";

  // 청록 계열: G가 B보다 크거나 거의 같음 (진짜 청록)
  if (g > 150 && b > 100 && r < g && g >= b - 10) return "청록 계열";

  // 진한 파랑 (B 우세, R/G 낮음)
  if (b > 100 && r < 50 && g < 100) return "진한 파랑 계열";

  // 파랑 계열: B 우세
  if (b > r && b > g) return "파랑 계열";

  // 핑크 계열: R 매우 높음 + G 중간 + B 중간~높음
  if (r > 200 && g > 100 && g < 200 && b > 150) return "핑크 계열";

  // 보라 계열: R, B 모두 높음 + G 매우 낮음
  if (r > 80 && b > 100 && g < 80 && r < b + 50) return "보라 계열";

  return "기타 색상";
}
