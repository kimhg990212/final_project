import os, itertools, requests, tqdm
import pandas as pd
from io import StringIO
from joblib import Parallel, delayed
from dotenv import load_dotenv
from sqlalchemy import text
from utils.database import engine  
import numpy as np
load_dotenv()

# 환경변수에서 읽기
api_keys = [
    key.strip()
    for key in os.getenv("KIPRIS_API_KEY", "").split(",")
    if key.strip()
]

if not api_keys:
    raise ValueError("KIPRIS_API_KEY 환경변수가 설정되지 않았습니다.")

# 무한 순환 iterator
key_cycle = itertools.cycle(api_keys)


def get_next_api_key():
    return next(key_cycle)

BASE_URL = "http://plus.kipris.or.kr/kipo-api/kipi"

def fetchTrademarkInfo(classification = "", page_no=1, num_of_rows=100):
    url = f"{BASE_URL}/trademarkInfoSearchService/getAdvancedSearch"

    params = {
        "classification": classification,   # 상품분류코드 → 업종(니스) 코드, 값을 비우면 전체(인자값으로 빈 문자열을 받았으니 전체를 가져옴)
        "application": "true", "registration": "true",   # application 출원 / registration 등록
        "pageNo": str(page_no), "numOfRows": str(num_of_rows),   # pageNo 페이지번호 / numOfRows 페이지당건수
        # 인증키
        "ServiceKey": get_next_api_key(),
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response

# res = fetchTrademarkInfo(page_no=1, num_of_rows=500)
# df = pd.read_xml(StringIO(res.text), xpath=".//item")

def parse_page(page_no, classification="", num_of_rows=500):
    res = fetchTrademarkInfo(
        classification=classification,
        page_no=page_no,
        num_of_rows=num_of_rows
    )
    try:
        df = pd.read_xml(StringIO(res.text), xpath=".//item")
        df = df.rename(columns={
            "applicationNumber": "application_number",
            "title": "title",
            "applicantName": "applicant_name",
            "applicationDate": "application_date",
            "classificationCode": "classification_code",
            "viennaCode": "vienna_code",
            "applicationStatus": "application_status",
            "drawing": "image_url",
            "bigDrawing": "big_image_url",
        })
        df = df[[
                "application_number","title","applicant_name",
                "application_date","classification_code",
                "vienna_code","application_status",
                "image_url","big_image_url"]]
        df = df.replace({np.nan: None})

        df["pageNo"] = page_no
        df["application_date"] = pd.to_datetime(
            df["application_date"],
            format="%Y%m%d",
            errors="coerce"
        ).dt.date
        items = df.to_dict(orient="records")
        sql = text("""
            INSERT INTO trademark_trends
            (application_number, title, applicant_name, application_date,
            classification_code, vienna_code, application_status,
            image_url, big_image_url)
            VALUES
            (:application_number, :title, :applicant_name, :application_date,
            :classification_code, :vienna_code, :application_status,
            :image_url, :big_image_url)
            ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            applicant_name = VALUES(applicant_name),
            application_status = VALUES(application_status),
            synced_at = NOW()
        """)
        with engine.begin() as conn:
            for item in items:
                conn.execute(sql, item)
    except Exception as e:
        return {"page_no": page_no, "error": str(e)}

parse_page(page_no=1, classification="", num_of_rows=500)

n_jobs = 5
results = Parallel(
    n_jobs=n_jobs,
    backend="threading"
)(
    delayed(parse_page)(
        page_no,
        classification="",
        num_of_rows=500
    )
    for page_no in tqdm.tqdm(range(21+180, 1000))
)
