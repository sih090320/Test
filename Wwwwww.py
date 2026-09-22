import streamlit as st
import requests
import datetime
import re

# ============================================================
# 페이지 설정
# ============================================================

st.set_page_config(
    page_title="보라고등학교 급식",
    page_icon="🍚",
    layout="centered"
)


# ============================================================
# 학교 정보
# ============================================================

# 경기도교육청
ATPT_CODE = "J10"

# 보라고등학교
SCHOOL_CODE = "7530882"

# NEIS 급식 API
API_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"


# ============================================================
# CSS 디자인
# ============================================================

st.markdown("""
<style>

    /* 전체 배경 */
    .stApp {
        background-color: #f7f8fa;
    }

    /* 제목 */
    .main-title {
        text-align: center;
        font-size: 38px;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    /* 부제 */
    .sub-title {
        text-align: center;
        color: #777777;
        font-size: 15px;
        margin-bottom: 25px;
    }

    /* 학교 정보 */
    .school-card {
        background: white;
        border-radius: 20px;
        padding: 22px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
        margin-bottom: 25px;
    }

    .school-name {
        font-size: 21px;
        font-weight: 700;
    }

    .school-code {
        color: #777777;
        margin-top: 8px;
        font-size: 14px;
    }

    /* 날짜 */
    .date-title {
        text-align: center;
        font-size: 23px;
        font-weight: 700;
        margin: 20px 0;
    }

    /* 급식 종류 */
    .meal-title {
        font-size: 25px;
        font-weight: 800;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    /* 메뉴 카드 */
    .menu-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
    }

    /* 음식 */
    .food-item {
        font-size: 18px;
        padding: 10px 2px;
        border-bottom: 1px solid #eeeeee;
    }

    .food-item:last-child {
        border-bottom: none;
    }

    /* 칼로리 */
    .calorie {
        background: #f1f3f5;
        border-radius: 12px;
        padding: 12px;
        margin-top: 15px;
        text-align: center;
        font-weight: 600;
    }

    /* 안내 */
    .info-card {
        background: white;
        border-radius: 18px;
        padding: 20px;
        text-align: center;
        color: #666666;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }

    /* 하단 */
    .footer {
        text-align: center;
        color: #999999;
        font-size: 13px;
        margin-top: 35px;
        margin-bottom: 20px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# NEIS 급식 데이터 가져오기
# ============================================================

@st.cache_data(ttl=1800)
def get_meal(date_string):

    params = {
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,

        # 경기도교육청
        "ATPT_OFCDC_SC_CODE": ATPT_CODE,

        # 보라고등학교
        "SD_SCHUL_CODE": SCHOOL_CODE,

        # 조회 날짜
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

        # ----------------------------------------------------
        # 급식 데이터가 정상적으로 있는 경우
        # ----------------------------------------------------

        if "mealServiceDietInfo" in data:

            meal_info = data["mealServiceDietInfo"]

            if len(meal_info) >= 2:

                rows = meal_info[1].get("row", [])

                return rows

        # ----------------------------------------------------
        # 급식이 없는 경우
        # ----------------------------------------------------

        return []

    except requests.exceptions.Timeout:

        return "TIMEOUT"

    except requests.exceptions.ConnectionError:

        return "CONNECTION_ERROR"

    except Exception:

        return "ERROR"


# ============================================================
# 메뉴 정리
# ============================================================

def clean_menu(menu_text):

    if not menu_text:
        return []

    # NEIS에서는 보통 <br/>로 메뉴를 구분함
    menus = re.split(
        r"<br\s*/?>",
        menu_text
    )

    result = []

    for menu in menus:

        menu = menu.strip()

        if not menu:
            continue

        # ----------------------------------------------------
        # 알레르기 번호 제거
        #
        # 예:
        # 김치찌개(5.6.9)
        # ↓
        # 김치찌개
        # ----------------------------------------------------

        menu = re.sub(
            r"\(\s*\d+(?:\.\d+)*\s*\)",
            "",
            menu
        )

        # 혹시 괄호 밖에 남아있는 알레르기 번호도 제거
        menu = re.sub(
            r"\d+(?:\.\d+)+",
            "",
            menu
        )

        # 여러 공백 정리
        menu = re.sub(
            r"\s+",
            " ",
            menu
        )

        menu = menu.strip()

        if menu:
            result.append(menu)

    return result


# ============================================================
# 제목
# ============================================================

st.markdown(
    '<div class="main-title">🍚 보라고등학교 급식</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">NEIS 학교급식 정보</div>',
    unsafe_allow_html=True
)


# ============================================================
# 학교 정보 카드
# ============================================================

st.markdown("""
<div class="school-card">

    <div class="school-name">
        🏫 보라고등학교
    </div>

    <div class="school-code">
        경기도교육청 · 학교코드 7530882
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# 날짜 선택
# ============================================================

today = datetime.date.today()

selected_date = st.date_input(
    "📅 날짜 선택",
    value=today,
    format="YYYY-MM-DD"
)


# ============================================================
# 날짜 빠른 선택 버튼
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    if st.button(
        "⬅️ 어제",
        use_container_width=True
    ):

        selected_date = selected_date - datetime.timedelta(days=1)

with col2:

    if st.button(
        "📅 오늘",
        use_container_width=True
    ):

        selected_date = today

with col3:

    if st.button(
        "내일 ➡️",
        use_container_width=True
    ):

        selected_date = selected_date + datetime.timedelta(days=1)


# ============================================================
# 선택 날짜 표시
# ============================================================

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
    <div class="date-title">
        {selected_date.strftime("%Y년 %m월 %d일")}
        <span style="color:#777777;">
            ({day_name})
        </span>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# NEIS 날짜 형식으로 변경
# ============================================================

date_string = selected_date.strftime("%Y%m%d")


# ============================================================
# 급식 조회
# ============================================================

with st.spinner("🍚 급식 정보를 불러오는 중..."):

    meals = get_meal(date_string)


# ============================================================
# 오류 처리
# ============================================================

if meals == "TIMEOUT":

    st.error(
        "⏰ NEIS 서버 응답 시간이 너무 오래 걸렸습니다."
    )

    st.stop()


if meals == "CONNECTION_ERROR":

    st.error(
        "🌐 NEIS 서버에 연결하지 못했습니다."
    )

    st.stop()


if meals == "ERROR":

    st.error(
        "❌ 급식 정보를 불러오는 중 오류가 발생했습니다."
    )

    st.stop()


# ============================================================
# 급식이 없는 경우
# ============================================================

if not meals:

    st.markdown(
        """
        <div class="info-card">

            🍽️ <b>해당 날짜의 급식 정보가 없습니다.</b>

            <br><br>

            주말, 공휴일, 방학 또는 급식이 없는 날일 수 있습니다.

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 급식 출력
# ============================================================

else:

    for meal in meals:

        # ----------------------------------------------------
        # 급식 종류
        # ----------------------------------------------------

        meal_name = meal.get(
            "MMEAL_SC_NM",
            "급식"
        )

        # ----------------------------------------------------
        # 메뉴
        # ----------------------------------------------------

        menu_text = meal.get(
            "DDISH_NM",
            ""
        )

        # ----------------------------------------------------
        # 칼로리
        # ----------------------------------------------------

        calorie = meal.get(
            "CAL_INFO",
            ""
        )

        # 메뉴 정리
        menus = clean_menu(menu_text)


        # ----------------------------------------------------
        # 급식 종류 제목
        # ----------------------------------------------------

        if meal_name == "조식":

            emoji = "🌅"

        elif meal_name == "중식":

            emoji = "🍱"

        elif meal_name == "석식":

            emoji = "🌙"

        else:

            emoji = "🍴"


        st.markdown(
            f"""
            <div class="meal-title">
                {emoji} {meal_name}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # 메뉴 HTML 만들기
        # ----------------------------------------------------

        menu_html = ""

        for food in menus:

            menu_html += f"""
            <div class="food-item">
                🍴 {food}
            </div>
            """


        # ----------------------------------------------------
        # 메뉴가 없는 경우
        # ----------------------------------------------------

        if not menu_html:

            menu_html = """
            <div class="food-item">
                급식 메뉴 정보가 없습니다.
            </div>
            """


        # ----------------------------------------------------
        # 칼로리
        # ----------------------------------------------------

        if calorie:

            calorie_html = f"""
            <div class="calorie">
                🔥 열량 : {calorie}
            </div>
            """

        else:

            calorie_html = """
            <div class="calorie">
                🔥 열량 정보 없음
            </div>
            """


        # ----------------------------------------------------
        # 메뉴 카드 출력
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div class="menu-card">

                {menu_html}

                {calorie_html}

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# 하단 안내
# ============================================================

st.markdown(
    """
    <div class="footer">

        🍚 보라고등학교 급식 정보<br>
        NEIS 학교급식 식단 정보를 기반으로 제공합니다.

    </div>
    """,
    unsafe_allow_html=True
)
