import { useEffect, useState } from "react";
import { getCategories, searchLogo, generateLogo } from "../api/recommend";

const BASE_URL = "http://localhost:5000";
const STEPS = ["업종 선택", "브랜드 설명", "TOP3 조회", "로고 생성"];

const STYLE_OPTIONS = ["아이콘만", "텍스트만", "아이콘+텍스트"];
const MOOD_OPTIONS = [
  "모던/미니멀",
  "클래식/전통",
  "귀여움/친근함",
  "고급스러움/럭셔리",
];
const COLOR_OPTIONS = ["밝은 계열", "어두운 계열", "단색", "컬러풀"];

function OptionButton({ label, selected, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "0.4rem 1rem",
        borderRadius: 20,
        border: selected ? "2px solid #333" : "1px solid #ccc",
        background: selected ? "#333" : "#fff",
        color: selected ? "#fff" : "#333",
        cursor: "pointer",
        fontSize: 14,
      }}
    >
      {label}
    </button>
  );
}

function RecommendPage({ userId }) {
  const [step, setStep] = useState(0);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [brandDescription, setBrandDescription] = useState("");
  const [selectedStyle, setSelectedStyle] = useState("");
  const [selectedMood, setSelectedMood] = useState("");
  const [selectedColor, setSelectedColor] = useState("");
  const [top3, setTop3] = useState([]);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch((e) => alert("카테고리 로딩 실패: " + e.message));
  }, []);

  const handleSearchTop3 = async () => {
    if (!selectedCategory) return alert("업종을 선택해주세요.");
    if (!brandDescription.trim()) return alert("브랜드 설명을 입력해주세요.");
    try {
      setLoading(true);
      const results = await searchLogo({
        categoryName: selectedCategory,
        brandDescription,
      });
      setTop3(results);
      setStep(2);
    } catch (e) {
      alert("TOP3 조회 실패: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setLoading(true);
      const ids = top3.map((r) => r.trademark_id);
      const images = await generateLogo({
        trademarkIds: ids,
        brandDescription,
        style: selectedStyle,
        mood: selectedMood,
        color: selectedColor,
      });
      setGeneratedImages(images);
      setStep(3);
    } catch (e) {
      alert("로고 생성 실패: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const getImageSrc = (url) => {
    if (!url) return "";
    if (url.startsWith("http")) return url;
    if (url.startsWith("/")) return `${BASE_URL}${url}`;
    return `${BASE_URL}/${url}`;
  };

  const handleDownload = (url, index) => {
    const link = document.createElement("a");
    link.href = getImageSrc(url);
    link.download = `logo_${index + 1}.png`;
    link.click();
  };

  const handleReset = () => {
    setStep(0);
    setTop3([]);
    setGeneratedImages([]);
    setBrandDescription("");
    setSelectedCategory("");
    setSelectedStyle("");
    setSelectedMood("");
    setSelectedColor("");
  };

  return (
    <main style={{ maxWidth: 800, margin: "0 auto", padding: "2rem" }}>
      <h1>로고 추천</h1>

      <div
        style={{
          display: "flex",
          gap: "1rem",
          marginBottom: "2rem",
          flexWrap: "wrap",
        }}
      >
        {STEPS.map((s, i) => (
          <div
            key={i}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: 20,
              background: step === i ? "#333" : "#eee",
              color: step === i ? "#fff" : "#999",
              fontSize: 14,
            }}
          >
            {i + 1}. {s}
          </div>
        ))}
      </div>

      {step <= 1 && (
        <section>
          <div style={{ marginBottom: "1.5rem" }}>
            <label
              style={{ display: "block", marginBottom: 8, fontWeight: "bold" }}
            >
              업종 선택
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setStep(1);
              }}
              style={{ width: "100%", padding: "0.5rem", fontSize: 16 }}
            >
              <option value="">-- 업종을 선택하세요 --</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label
              style={{ display: "block", marginBottom: 8, fontWeight: "bold" }}
            >
              스타일
            </label>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {STYLE_OPTIONS.map((opt) => (
                <OptionButton
                  key={opt}
                  label={opt}
                  selected={selectedStyle === opt}
                  onClick={() =>
                    setSelectedStyle(selectedStyle === opt ? "" : opt)
                  }
                />
              ))}
            </div>
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label
              style={{ display: "block", marginBottom: 8, fontWeight: "bold" }}
            >
              분위기
            </label>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {MOOD_OPTIONS.map((opt) => (
                <OptionButton
                  key={opt}
                  label={opt}
                  selected={selectedMood === opt}
                  onClick={() =>
                    setSelectedMood(selectedMood === opt ? "" : opt)
                  }
                />
              ))}
            </div>
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label
              style={{ display: "block", marginBottom: 8, fontWeight: "bold" }}
            >
              색상 계열
            </label>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {COLOR_OPTIONS.map((opt) => (
                <OptionButton
                  key={opt}
                  label={opt}
                  selected={selectedColor === opt}
                  onClick={() =>
                    setSelectedColor(selectedColor === opt ? "" : opt)
                  }
                />
              ))}
            </div>
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label
              style={{ display: "block", marginBottom: 8, fontWeight: "bold" }}
            >
              브랜드 설명
            </label>
            <textarea
              placeholder="예: 고급스러운 분위기의 카페, 브라운과 골드 컬러, 미니멀한 스타일"
              value={brandDescription}
              onChange={(e) => setBrandDescription(e.target.value)}
              rows={4}
              style={{ width: "100%", padding: "0.5rem", fontSize: 15 }}
            />
          </div>

          <button
            onClick={handleSearchTop3}
            disabled={loading}
            style={{
              padding: "0.75rem 2rem",
              background: "#333",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontSize: 16,
              cursor: "pointer",
            }}
          >
            {loading ? "조회 중..." : "TOP3 조회하기"}
          </button>
        </section>
      )}

      {step === 2 && (
        <section>
          <h2>비유사 TOP3 상표</h2>
          <div
            style={{
              display: "flex",
              gap: "1rem",
              marginBottom: "2rem",
              flexWrap: "wrap",
            }}
          >
            {top3.map((item) => (
              <div
                key={item.trademark_id}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: 8,
                  padding: "1rem",
                  width: 200,
                  textAlign: "center",
                }}
              >
                {item.image_url && (
                  <img
                    src={item.image_url}
                    alt={item.title}
                    style={{ width: "100%", height: 120, objectFit: "contain" }}
                  />
                )}
                <p style={{ fontSize: 14, marginTop: 8 }}>{item.title}</p>
                <p style={{ fontSize: 12, color: "#999" }}>
                  유사도: {item.similarity_score}
                </p>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: "1rem" }}>
            <button
              onClick={() => setStep(0)}
              style={{
                padding: "0.75rem 2rem",
                background: "#eee",
                border: "none",
                borderRadius: 8,
                fontSize: 16,
                cursor: "pointer",
              }}
            >
              다시 입력
            </button>
            <button
              onClick={handleGenerate}
              disabled={loading}
              style={{
                padding: "0.75rem 2rem",
                background: "#333",
                color: "#fff",
                border: "none",
                borderRadius: 8,
                fontSize: 16,
                cursor: "pointer",
              }}
            >
              {loading ? "생성 중... (1~3분 소요)" : "로고 생성하기"}
            </button>
          </div>
        </section>
      )}

      {step === 3 && (
        <section>
          <h2>생성된 로고</h2>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
            {generatedImages.map((imgUrl, i) => (
              <div key={i} style={{ textAlign: "center" }}>
                <img
                  src={getImageSrc(imgUrl)}
                  alt={`생성 로고 ${i + 1}`}
                  style={{
                    width: 300,
                    height: 300,
                    objectFit: "contain",
                    border: "1px solid #ddd",
                  }}
                />
                <div style={{ marginTop: 8 }}>
                  <button
                    onClick={() => handleDownload(imgUrl, i)}
                    style={{
                      padding: "0.5rem 1.5rem",
                      background: "#333",
                      color: "#fff",
                      border: "none",
                      borderRadius: 8,
                      fontSize: 14,
                      cursor: "pointer",
                    }}
                  >
                    저장하기
                  </button>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={handleReset}
            style={{
              marginTop: "2rem",
              padding: "0.75rem 2rem",
              background: "#eee",
              border: "none",
              borderRadius: 8,
              fontSize: 16,
              cursor: "pointer",
            }}
          >
            처음부터 다시
          </button>
        </section>
      )}
    </main>
  );
}

export default RecommendPage;
