import streamlit as st
import requests
import pandas as pd
import datetime
import re

# -----------------------
# 설정
# -----------------------
ATPT_CODE = "J10"      # 경기도교육청
SCHOOL_CODE = "7530882"  # 보라고등학교

API_KEY = st.secrets["NEIS_API_KEY"]

st.set_page_config(
    page_title="보라고등학교 급식",
    page_icon="🍚",
    layout="centered"
)

st.title("🍚 보라고등학교 급식 정보")
st.caption("NEIS Open API 사용")

# -----------------------
# 날짜 선택
# -----------------------
selected_date = st.date_input(
    "날짜 선택",
    datetime.date.today()
)

date_str = selected_date.strftime("%Y%m%d")

# -----------------------
# 급식 조회 함수
# -----------------------
@st.cache_data(ttl=3600)
def get_meal(date):
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"

    params = {
        "KEY": API_KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": ATPT_CODE,
        "SD_SCHUL_CODE": SCHOOL_CODE,
        "MLSV_YMD": date
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    data = response.json()

    try:
        rows = data["mealServiceDietInfo"][1]["row"]
        return rows
    except:
        return None

# -----------------------
# 메뉴 정리 함수
# -----------------------
def clean_menu(menu):
    items = menu.split("<br/>")

    cleaned = []

    for item in items:
        # 알레르기 숫자 제거
        item = re.sub(r"\d+\.", "", item)

        # 괄호 제거
        item = re.sub(r"\([^)]*\)", "", item)

        cleaned.append(item.strip())

    return cleaned

# -----------------------
# 조회
# -----------------------
meal_data = get_meal(date_str)

if meal_data:

    for meal in meal_data:

        st.subheader(meal["MMEAL_SC_NM"])

        menu = clean_menu(meal["DDISH_NM"])

        for food in menu:
            st.write("•", food)

        if "CAL_INFO" in meal:
            st.info(f"🔥 칼로리: {meal['CAL_INFO']}")

        st.divider()

else:
    st.warning("해당 날짜의 급식 정보가 없습니다.")
