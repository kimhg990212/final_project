import { useState } from "react";

import { generateTextLogo, saveDownloadHistory } from "../api/text_logo";
import "../css/generate.css";

const BASE_URL = "http://localhost:5000";

function GeneratePage({ userId, googleToken }) {
  const [text, setText] = useState("");
  const [logoName, setLogoName] = useState("");
  const [result, setResult] = useState(null);
  const [mode, setMode] = useState("text");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [resultImage, setResultImage] = useState(null); //파일 기반 이미지 결과 state

  const handleGenerate = async () => {
    if (mode === "text") {
      //텍스트 모드 분기로 감쌈
      if (!logoName.trim()) {
        alert("상표명을 입력해주세요.");
        return;
      }
      if (!text.trim()) {
        alert("로고 설명을 입력해주세요.");
        return;
      }
      try {
        setLoading(true);
        const data = await generateTextLogo({ logoName, text, userId });
        setResult({
          resultId: data.id ?? null,
          logoName,
          prompt: text,
          image_url: data.image_url || data.image_path,
        });
      } catch (err) {
        alert(err.message);
      } finally {
        setLoading(false);
      }
      return;
    }

    // 파일 기반 생성 API 호출
    if (!file) {
      alert("파일을 선택해주세요.");
      return;
    }
    if (!text.trim()) {
      alert("추가 설명을 입력해주세요.");
      return;
    }

    try {
      setLoading(true);
      setResultImage(null);

      const formData = new FormData();
      formData.append("file", file);
      const uploadRes = await fetch(`${BASE_URL}/Upload/upload`, {
        method: "POST",
        body: formData,
      });
      if (!uploadRes.ok) {
        const err = await uploadRes.json();
        throw new Error(err.detail || "파일 업로드 실패");
      }
      const fileId = (await uploadRes.json()).id;

      const generateRes = await fetch(`${BASE_URL}/Upload/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_id: fileId, prompt: text }),
      });
      if (!generateRes.ok) {
        const err = await generateRes.json();
        throw new Error(err.detail || "생성 요청 실패");
      }
      const resultId = (await generateRes.json()).id;

      let resultContent = null;
      for (let i = 0; i < 60; i++) {
        await new Promise((res) => setTimeout(res, 1000));
        const resultRes = await fetch(`${BASE_URL}/Upload/result/${resultId}`);
        if (!resultRes.ok) continue;
        const resultData = await resultRes.json();
        if (
          resultData.result_image &&
          resultData.result_image !== "처리 중..."
        ) {
          resultContent = resultData.result_image;
          break;
        }
      }

      if (!resultContent)
        throw new Error("생성 시간이 초과됐습니다. 다시 시도해주세요.");
      setResultImage(resultContent);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getImageSrc = (imageUrl) => {
    if (!imageUrl) return "";
    if (imageUrl.startsWith("http")) return imageUrl;
    return `${BASE_URL}/${imageUrl}`;
  };

  const handleDownload = async () => {
    if (!result?.image_url) {
      alert("다운로드할 이미지가 없습니다.");
      return;
    }
    try {
      const response = await fetch(getImageSrc(result.image_url));
      if (!response.ok) throw new Error("이미지 다운로드에 실패했습니다.");
      const blob = await response.blob();
      await saveDownloadHistory({
        token: googleToken,
        userId,
        resultId: result.resultId ?? null,
        prompt: result.prompt || text,
        imagePath: result.image_url,
      });
      const downloadUrl = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = downloadUrl;
      anchor.download = `logo-${Date.now()}.png`;
      anchor.click();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "이미지 다운로드에 실패했습니다.",
      );
    }
  };

  return (
    <main className="generate-page">
      <section className="generate-header">
        <span>AI Logo Generator</span>
        <h1>
          {mode === "text" ? "텍스트 기반 로고 생성" : "파일 기반 로고 생성"}
        </h1>
        <p>
          {mode === "text"
            ? "브랜드 설명을 입력하면 AI가 로고 이미지를 생성합니다."
            : "업로드한 이미지나 문서를 참고하여 AI가 로고 이미지를 생성합니다."}
        </p>
      </section>

      <div className="generate-tabs">
        <button
          className={mode === "text" ? "active" : ""}
          onClick={() => {
            setMode("text");
            setResult(null);
            setResultImage(null);
          }} //setResultImage(null) 추가
        >
          텍스트 기반 생성
        </button>
        <button
          className={mode === "file" ? "active" : ""}
          onClick={() => {
            setMode("file");
            setResult(null);
            setResultImage(null);
          }} //setResultImage(null) 추가
        >
          파일 기반 생성
        </button>
      </div>

      <section className="generate-layout">
        <div className="generate-panel">
          <h2>생성 정보 입력</h2>

          {mode === "text" ? (
            <>
              <label>상표명</label>
              <input
                type="text"
                placeholder="예: 멍멍마켓"
                value={logoName}
                onChange={(e) => setLogoName(e.target.value)}
              />
              <label>로고 설명</label>
              <textarea
                placeholder="예: 고급스러운 분위기의 카페 로고, 브라운과 골드 컬러, 미니멀한 스타일"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            </>
          ) : (
            <>
              <label>참고 파일 업로드</label>
              <div className="upload-box">
                <input
                  type="file"
                  accept="image/*,.txt,.docx,.pdf"
                  onChange={(e) => setFile(e.target.files[0])}
                />
                <p>{file ? file.name : "이미지 또는 문서를 업로드하세요"}</p>
              </div>
              <label>추가 설명</label>
              <textarea
                placeholder="예: 업로드한 이미지를 참고해서 더 세련되게 생성"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            </>
          )}

          <div className="tip-box">
            <strong>TIP</strong>
            <p>
              {mode === "text"
                ? "업종, 색상, 분위기, 스타일을 함께 입력하면 결과가 좋아집니다."
                : "참고 이미지와 함께 원하는 스타일을 설명하면 결과가 더 정확합니다."}
            </p>
          </div>

          <button
            className="generate-btn"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? "생성 중.." : "생성하기"}
          </button>
        </div>

        <div className="result-panel">
          <h2>생성 결과</h2>

          {/*mode 분기 추가, 파일 모드에서 base64 이미지 표시 */}
          <div className="result-image-box">
            {mode === "text" ? (
              result?.image_url ? (
                <div className="image-wrapper">
                  <img
                    src={getImageSrc(result.image_url)}
                    alt="생성된 로고"
                    className="generated-logo-img"
                    onContextMenu={(e) => e.preventDefault()}
                    onDragStart={(e) => e.preventDefault()}
                  />
                  <div className="watermark">PREVIEW</div>
                </div>
              ) : loading ? (
                <p>이미지를 생성하는 중입니다...</p>
              ) : (
                <p>아직 생성된 이미지가 없습니다.</p>
              )
            ) : resultImage ? (
              <img
                src={`data:image/png;base64,${resultImage}`}
                alt="생성된 이미지"
                style={{ width: "100%" }}
              />
            ) : loading ? (
              <p>이미지를 생성하는 중입니다...</p>
            ) : (
              <p>아직 생성된 이미지가 없습니다.</p>
            )}
          </div>

          {/* mode === "text" 조건 추가 */}
          {mode === "text" && result && (
            <div className="result-info">
              <p>
                <strong>상표명</strong>
                {result.logoName}
              </p>
              <p>
                <strong>입력 내용</strong>
                {result.prompt || "입력된 설명 없음"}
              </p>
              {mode === "file" && file && (
                <p>
                  <strong>참고 파일</strong>
                  {file.name}
                </p>
              )}
              <button onClick={handleDownload} className="save-btn">
                저장하기
              </button>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

export default GeneratePage;
