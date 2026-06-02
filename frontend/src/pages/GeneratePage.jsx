import { useState } from "react";
import "../css/generate.css";

function GeneratePage() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [mode, setMode] = useState("text");
  const [file, setFile] = useState(null);

  const handleGenerate = () => {
    setResult({
      prompt: text,
      image_url: "",
    });
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
            }}
          >
            텍스트 기반 생성
          </button>

          <button
            className={mode === "file" ? "active" : ""}
            onClick={() => {
              setMode("file");
              setResult(null);
            }}
          >
            파일 기반 생성
          </button>
        </div>

        <section className="generate-layout">
          {/* 왼쪽 입력 영역 */}
          <div className="generate-panel">
            <h2>생성 정보 입력</h2>

            {mode === "text" ? (
              <>
                <label>로고 설명</label>

                <textarea
                  placeholder="예: 고급스러운 밀크티 카페 로고, 브라운과 골드 컬러, 심플한 엠블럼 느낌"
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
                  placeholder="예: 업로드한 이미지의 분위기를 참고해서 더 심플하게 생성"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                />
              </>
            )}

            <div className="tip-box">
              <strong>TIP</strong>

              <p>
                {mode === "text"
                  ? "업종, 색상, 분위기, 원하는 심볼을 함께 입력하면 결과가 좋아집니다."
                  : "참고 이미지와 함께 원하는 스타일을 설명하면 결과 품질이 향상됩니다."}
              </p>
            </div>

            <button className="generate-btn" onClick={handleGenerate}>
              생성하기
            </button>
          </div>

          {/* 오른쪽 결과 영역 */}
          <div className="result-panel">
            <h2>생성 결과</h2>

            <div className="result-image-box">
              {result ? (
                <div className="mock-logo">
                  {mode === "text" ? "TEXT LOGO" : "FILE LOGO"}
                </div>
              ) : (
                <p>아직 생성된 이미지가 없습니다.</p>
              )}
            </div>

            {result && (
              <div className="result-info">
                <p>
                  <strong>입력 내용</strong>

                  {text || "입력된 설명 없음"}
                </p>

                {mode === "file" && file && (
                  <p>
                    <strong>업로드 파일</strong>

                    {file.name}
                  </p>
                )}

                <button className="save-btn">저장하기</button>
              </div>
            )}
          </div>
        </section>
    </main>
  );
}

export default GeneratePage;
