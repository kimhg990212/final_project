import { useEffect, useState } from "react";
import { getCategories, searchLogo, generateLogo } from "../api/recommend";

const BASE_URL = "http://localhost:5000";
const STEPS = ["커스터마이징", "병합이미지 추천", "로고 생성"];

const STYLE_OPTIONS = ["이미지", "이미지+텍스트"];

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
  const [top3, setTop3] = useState([]);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

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
        style: selectedStyle,
      });
      setTop3(results);
      setStep(1);
    } catch (e) {
      alert("병합이미지 추천 실패: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setIsGenerating(true);
      const ids = top3.map((r) => r.trademark_id);
      const images = await generateLogo({
        trademarkIds: ids,
        brandDescription,
        style: selectedStyle,
      });
      setGeneratedImages(images);
      setStep(2);
    } catch (e) {
      alert("로고 생성 실패: " + e.message);
    } finally {
      setLoading(false);
      setIsGenerating(false);
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
    setIsGenerating(false);
  };

  return (
    <main style={{ maxWidth: 800, margin: "0 auto", padding: "2rem" }}>
      {isGenerating && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.65)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
          }}
        >
          <div
            style={{
              background: "#fff",
              borderRadius: 16,
              padding: "3rem 4rem",
              textAlign: "center",
              boxShadow: "0 8px 32px rgba(0,0,0,0.2)",
            }}
          >
            <div
              style={{
                width: 56,
                height: 56,
                border: "5px solid #eee",
                borderTop: "5px solid #333",
                borderRadius: "50%",
                margin: "0 auto 1.5rem",
                animation: "spin 0.9s linear infinite",
              }}
            />
            <h2 style={{ margin: 0, marginBottom: 8, fontSize: 22 }}>
              로고 생성 중...
            </h2>
            <p style={{ color: "#888", margin: 0, fontSize: 14 }}>
              1~3분 정도 소요될 수 있습니다
            </p>
          </div>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      )}

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

      {step === 0 && (
        <section>
          <div style={{ marginBottom: "1.5rem" }}>
            <label
              style={{ display: "block", marginBottom: 8, fontWeight: "bold" }}
            >
              업종 선택
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
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
              브랜드 설명
            </label>
            <textarea
              placeholder="예: 애견카페, 애견용품점"
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
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "조회 중..." : "병합이미지 추천 받기"}
          </button>
        </section>
      )}

      {step === 1 && (
        <section>
          <h2>참고 TOP3 상표</h2>
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
                {selectedStyle === "이미지+텍스트" && (
                  <>
                    <p style={{ fontSize: 14, marginTop: 8 }}>{item.title}</p>
                    <p style={{ fontSize: 12, color: "#999" }}>
                      유사도: {item.similarity_score}
                    </p>
                  </>
                )}
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
                cursor: loading ? "not-allowed" : "pointer",
              }}
            >
              로고 생성하기
            </button>
          </div>
        </section>
      )}

      {step === 2 && (
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
