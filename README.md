# 🕵️ 마크랩(Mark Lab)

본 프로젝트는 *상표권 및 디자인 도용 탐지*를 위한 서비스입니다.

---

![시연](./resource/시연.gif)

<div style="display: flex; align-items: center; gap: 8px;">
  <div>
    <img src="https://img.shields.io/badge/Licence-GPL-1177AA.svg?style=flat-round" />
    <img src="https://img.shields.io/badge/OpenAI-412991?logo=openai&logoColor=white" />
    <img src="https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white" />
    <img src="https://img.shields.io/badge/TensorFlow-FF6F00?logo=tensorflow&logoColor=white" />
    <img src="https://img.shields.io/badge/Transformers-FFD21E?logo=huggingface&logoColor=black" />
    <img src="https://img.shields.io/badge/HuggingFace-FFD21E?logo=huggingface&logoColor=black" />
    <img src="https://img.shields.io/badge/FFmpeg-007808?logo=ffmpeg&logoColor=white" />
    <img src="https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white" />
    <img src="https://img.shields.io/badge/Version-0.0.1-1177AA.svg?style=flat-round" />
    <img
        src="https://img.shields.io/badge/HTML-%23E34F26.svg?logo=html5&logoColor=white" alt="HTML" />
    <img
      src="https://img.shields.io/badge/CSS-1572B6?style=flat&logo=CSS&logoColor=white" alt="CSS Badge" />
    <img
    src="https://img.shields.io/badge/JavaScript-%23F7DF1E.svg?logo=javascript&logoColor=black" alt="JavaScript" />
    <img src="https://img.shields.io/badge/react-1177AA?logo=react&logoColor=%2361DAFB" alt="React" />
    <br/>
    <img src="https://img.shields.io/badge/python-3.10.18-1177AA.svg?style=flat-round" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-02569B?logo=FastAPI&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/github-%23121011?logo=github&logoColor=white" alt="GitHub" />
    <img src="https://img.shields.io/badge/Docker-1572B6?logo=docker&logoColor=fff" />
    <img src="https://img.shields.io/badge/Docker--Compose-000000?logo=docker&logoColor=white" />
    <img src="https://img.shields.io/badge/MySQL-1572B6?logo=mysql&logoColor=fff" />

  </div>
</div>

## 💡 개발 배경 및 목적

- 브랜드 및 디지털 자산의 생산 속도가 빠르게 증가함에 따라 지식재산권 도용 사례 또한 지속적으로 늘어나고 있다. 이에 따라 지식재산권 보호의 중요성이 더욱 커지고 있다.
- 현재 상표 및 디자인 침해에 대한 대응은 수작업 모니터링 중심으로 이루어져 탐지 속도와 정확도에 한계가 존재한다.
- 상표 도용 탐지 기술 개발 및 상표 생성 서비스를 제공함으로써 건강한 지식재산권 생태계 조성에 기여하는 것을 목표로한다.

## ⚙️ 서비스 핵심 기능

**[주요기능]**

1. 편리한 상표권 조회: 업종/업태별로 상표들을 조회해 참고함으로써 나만의 새로운 브랜드 상표 이미지를 빠르게 구상할 수 있습니다.
2. 상표권 도용 탐지: 내가 만들고자하는 새로운 브랜드 상표 이미지가 기존 등록된 상표에 디자인적으로 침해되는지를 확인할 수 있습니다.
3. 상표 이미지 생성: 복잡한 절차나 과정없이 프롬프트 입력을 통해 내가 원하는 상표 이미지를 생성할 수 있습니다.

## 📆 개발 과정

- 개발 기간은 5월 11일부터 6월 22일까지 진행(팀 배정 및 주제선정, 발표 자료 작성 기간 포함)
- 개발 과정은 오전 회의 진행, 및 오전/오후 일정 파악 수행

## 📦 설치 및 실행

```bash
# 저장소 복제
git clone https://github.com/kimhg990212/final_project

# 폴더 이동
cd final_project

```

### frontend 실행

```bash
# 폴더 이동
cd frontend
# 프로젝트 실행
npm run dev
```

### backend 설치

[faiss_text](https://drive.google.com/file/d/131Bd7yZPfyC2pI3nX439SXyU-IbRe4cN/view?usp=sharing)

[faiss_image](https://drive.google.com/file/d/1EI63FpxH6hh0u_Ynxb4OSrUvlQPBe9gJ/view?usp=sharing)

```bash
# 폴더 이동
cd backend
# 가상환경 생성
conda create final_pj_py312 python==3.12 -y
# 가상환경 활성화
conda activate final_pj_py312
# 패키지 설치
pip install -r requirements.txt
# vector store 다운로드
# backend/index 폴더로 이동
# backend/index
# ㄴ faiss_image.index
# ㄴ faiss_text.index
```

### backend 실행

```bash
# 폴더 이동
cd backend
# 프로젝트 실행
python main.py
```

### 개발 관련 가이드라인

- [코드 관련 가이드라인](https://github.com/kimhg990212/final_project/blob/main/resource/guides/CODE_DOCS.md)
- [git 메세지 관련 가이드 라인](https://github.com/kimhg990212/final_project/blob/main/resource/guides/GIT_메세지작성.md)

## 🚧 향후 개발 계획

## ©️License

본 프로젝트의 코드는 비상업적 용도로 자유롭게 사용하실 수 있습니다.
상업적 이용이나 수정, 재배포 시에는 사전 연락을 부탁드립니다.

## 📖 Reference

- 데이터 출처 : [지식재산정보 활용 서비스](https://plus.kipris.or.kr/portal/main.do)
- 파비콘 출처 : [파비콘](https://www.flaticon.com/kr/free-icons/)

## 👨‍💻👩‍💻 Collaborator

- [정진화]()
- [김소현]()
- [김효균]()
- [이민혁]()
- [이동원]()
- [김준서]()
