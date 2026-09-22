import streamlit as st
import requests
import datetime
import re

# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="보라고등학교 급식",
    page_icon="🍚",
    layout="centered"
)

# 보라고등학교 정보
ATPT_CODE = "J10"          # 경기도교육청
SCHOOL_CODE = "7530882"    # 보라고등학교

# =========================================================
# CSS - 화면 디자인
# =========================================================

st.markdown("""
<style>

    .main {
        background-color: #f7f8fa;
    }

    .title {
        text-align: center;
        font-size: 36px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #777777;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .school-box {
        background: white;
        padding: 20px;
        border-radius: 18px;
        margin-bottom: 20px;
        box-shadow: 0px 3px 12px rgba(0,0,0,0.07);
        text-align: center;
    }

    .meal-title {
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .menu-box {
        background: white;
        padding: 20px;
        border-radius: 18px;
        margin-top: 10px;
        margin-bottom: 18px;
        box-shadow: 0px 3px 12px rgba(0,0,0,0.06);
    }

    .food {
        font-size: 18px;
        padding: 7px 0;
        border-bottom: 1px solid #eeeeee;
    }

    .calorie {
        margin-top: 15px;
        padding: 10px;
        border-radius: 10px;
        background-color: #f1f3f5;
        text-align: center;
        font-weight: 600;
    }

    .footer {
        text-align: center;
        color: #999999;
        font-size: 13px;
        margin-top: 30px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# NEIS API KEY 가져오기
# =========================================================

try:
    API_KEY = st.secrets["NEIS_API_KEY"]

except KeyError:
    st.error("⚠️ NEIS API 키가 설정되지 않았습니다.")

    st.markdown("""
    ### Streamlit Cloud 설정 방법

    1. Streamlit Cloud에서 현재 앱을 선택합니다.
    2. **Manage app**을 누릅니다.
    3. **Settings → Secrets**로 들어갑니다.
    4. 아래 내용을 입력합니다.

    ```toml
    NEIS_API_KEY = "발급받은_API_키"
    ```

    5. 저장한 후 앱을 다시 실행합니다.
    """)

    st.stop()


# =========================================================
# NEIS 급식 API
# =========================================================

API_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"


@st.cache_data(ttl=3600)
def get_meal(date_string):

    params = {
        "KEY": API_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": ATPT_CODE,
        "SD_SCHUL_CODE": SCHOOL_CODE,
        "MLSV_YMD": date_string
    }

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        # 정상적인 급식 데이터가 있는 경우
        if "mealServiceDietInfo" in data:

            meal_info = data["mealServiceDietInfo"]

            if len(meal_info) >= 2:

                rows = meal_info[1].get("row", [])

                return rows

        # NEIS가 ERROR를 반환하는 경우
        return []

    except requests.exceptions.RequestException as e:

        st.error("❌ NEIS 서버에 연결하지 못했습니다.")

        return []

    except Exception:

        st.error("❌ 급식 정보를 불러오는 중 오류가 발생했습니다.")

        return []


# =========================================================
# 메뉴 정리
# =========================================================

def clean_menu(menu_text):

    if not menu_text:
        return []

    # <br/> 기준으로 메뉴 분리
    menus = re.split(r"<br\s*/?>", menu_text)

    result = []

    for menu in menus:

        menu = menu.strip()

        if not menu:
            continue

        # 알레르기 번호 제거
        # 예: 김치찌개(5.6.9) → 김치찌개
        menu = re.sub(
            r"\(\s*\d+(?:\.\d+)*\s*\)",
            "",
            menu
        )

        # 혹시 남아있는 알레르기 번호 제거
        menu = re.sub(
            r"\d+(?:\.\d+)+",
            "",
            menu
        )

        menu = menu.strip()

        if menu:
            result.append(menu)

    return result


# =========================================================
# 화면
# =========================================================

st.markdown(
    '<div class="title">🍚 보라고등학교 급식</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">NEIS 학교급식 정보 서비스</div>',
    unsafe_allow_html=True
)


# =========================================================
# 학교 정보
# =========================================================

st.markdown("""
<div class="school-box">

<b>🏫 보라고등학교</b><br>

경기도교육청 · 학교코드 7530882

</div>
""", unsafe_allow_html=True)


# =========================================================
# 날짜 선택
# =========================================================

today = datetime.date.today()

selected_date = st.date_input(
    "📅 급식 날짜",
    value=today,
    format="YYYY-MM-DD"
)

date_string = selected_date.strftime("%Y%m%d")


# =========================================================
# 오늘 버튼
# =========================================================

if st.button("📅 오늘 급식 보기", use_container_width=True):

    selected_date = today

    date_string = selected_date.strftime("%Y%m%d")

    st.rerun()


# =========================================================
# 선택한 날짜 표시
# =========================================================

day_names = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

day_name = day_names[selected_date.weekday()]

st.markdown(
    f"""
    <div style="
        text-align:center;
        font-size:20px;
        font-weight:700;
        margin:20px 0;
    ">
        {selected_date.strftime("%Y년 %m월 %d일")}
        <span style="color:#777;">({day_name})</span>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 급식 가져오기
# =========================================================

with st.spinner("🍚 급식 정보를 불러오는 중..."):

    meals = get_meal(date_string)


# =========================================================
# 급식 출력
# =========================================================

if not meals:

    st.info(
        "🍽️ 해당 날짜에는 등록된 급식 정보가 없습니다.\n\n"
        "주말이나 공휴일, 방학일에는 급식이 없을 수 있습니다."
    )

else:

    for meal in meals:

        meal_name = meal.get(
            "MMEAL_SC_NM",
            "급식"
        )

        menu_text = meal.get(
            "DDISH_NM",
            ""
        )

        calorie = meal.get(
            "CAL_INFO",
            ""
        )

        menus = clean_menu(menu_text)

        # 급식 종류
        st.markdown(
            f"""
            <div class="meal-box">
                <div class="meal-title">
                    🍱 {meal_name}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 메뉴
        menu_html = ""

        for food in menus:

            menu_html += f"""
            <div class="food">
                🍴 {food}
            </div>
            """

        if not menu_html:

            menu_html = """
            <div class="food">
                급식 메뉴 정보가 없습니다.
            </div>
            """

        st.markdown(
            f"""
            <div class="menu-box">

                {menu_html}

                <div class="calorie">
                    🔥 {calorie if calorie else "칼로리 정보 없음"}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# 하단
# =========================================================

st.markdown(
    """
    <div class="footer">
        급식 정보는 NEIS 학교급식 식단 정보를 기반으로 제공합니다.<br>
        실제 급식과 일부 차이가 있을 수 있습니다.
    </div>
    """,
    unsafe_allow_html=True
)
