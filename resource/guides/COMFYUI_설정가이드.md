# ComfyUI 및 AI 환경 설정 가이드

## 개요

본 프로젝트의 **상표(로고) 생성 기능**은 ComfyUI와 Stable Diffusion XL(SDXL)을 기반으로 동작합니다.

따라서 프로젝트를 실행하기 전에 ComfyUI 서버를 실행하고, `.env` 파일에 해당 서버 주소를 등록해야 합니다.

---

## 1. `.env` 파일 생성

`backend/.env.sample` 파일을 복사하여 `.env` 파일을 생성합니다.

```text
backend/
├── .env.sample
└── .env
```

---

## 2. ComfyUI 실행

각 개발자는 공유받은 ComfyUI 서버를 사용할 수 있습니다.

ComfyUI가 정상적으로 실행되면 ngrok 등을 이용하여 외부 접속 주소를 생성합니다.

예시)

```text
https://xxxx-xxxx.ngrok-free.app
```

---

## 3. COMFYUI_URL 등록

sample에 있는 주소를 `backend/.env` 파일에 입력합니다.

```env
COMFYUI_URL=https://xxxx-xxxx.ngrok-free.app
```

---

## 4. Backend 실행

```bash
cd backend

conda activate final_pj_py312

python main.py
```

또는

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

---

## 5. 정상 동작 확인

1. 로그인
2. 로고 생성 페이지 이동
3. 프롬프트 입력
4. 이미지 생성 버튼 클릭

정상적으로 설정된 경우 생성된 이미지가 화면에 출력됩니다.

---

## 주의사항

- `.env` 파일은 Git에 포함되지 않습니다.
- `.env.sample`은 예시 파일이며 실제 값을 입력하지 않습니다.
- ComfyUI 서버가 실행되지 않은 경우 로고 생성 기능은 동작하지 않습니다.
- ngrok 주소가 변경되면 `.env`의 `COMFYUI_URL`도 함께 수정해야 합니다.

---

## 개발자 참고

프로젝트를 처음 Pull 받은 경우 아래 순서대로 진행하면 됩니다.

```text
1. git pull
2. backend/.env.sample → .env 복사
3. COMFYUI_URL 입력
4. backend/index 폴더에 faiss 파일 배치
5. Backend 실행
6. Frontend 실행
```

위 과정을 완료하면 로고 생성 기능을 포함한 전체 서비스를 정상적으로 사용할 수 있습니다.
