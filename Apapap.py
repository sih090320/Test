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

# =========================================================
# 보라고등학교 정보
# =========================================================

ATPT_CODE = "J10"
SCHOOL_CODE = "7530882"

# ⭐ 여기에 NEIS API 인증키를 직접 입력
API_KEY = "YOUR_NEIS_API_KEY"


# =========================================================
# CSS
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
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #777777;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .school-box {
        background-color: white;
        padding: 20px;
        border-radius: 18px;
        margin-bottom: 20px;
        box-shadow: 0px 3px 12px rgba(0,0,0,0.07);
        text-align: center;
        font-size: 17px;
    }

    .date-box {
        text-align: center;
        font-size: 21px;
        font-weight: 700;
        margin: 20px 0;
    }

    .meal-title {
        font-size: 25px;
        font-weight: 800;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .menu-box {
        background-color: white;
        padding: 18px 20px;
        border-radius: 18px;
        margin-bottom: 20px;
        box-shadow: 0px 3px 12px rgba(0,0,0,0.06);
    }

    .food {
        font-size: 18px;
        padding: 8px 0;
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
        margin-bottom: 20px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# API 키 확인
# =========================================================

if API_KEY == "YOUR_NEIS_API_KEY":

    st.error("⚠️ NEIS API 키를 코드에 입력해주세요.")

    st.code(
        'API_KEY = "YOUR_NEIS_API_KEY"',
        language="python"
    )

    st.stop()


# =========================================================
# NEIS API 주소
# =========================================================

API_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"


# =========================================================
# 급식 조회 함수
# =========================================================

@st.cache_data(ttl=1800)
def get_meal(date_string):

    params = {
        "KEY": API_KEY,
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

        # ---------------------------------------------
        # 정상적인 급식 데이터
        # ---------------------------------------------

        if "mealServiceDietInfo" in data:

            meal_info = data["mealServiceDietInfo"]

            if len(meal_info) >= 2:

                rows = meal_info[1].get("row", [])

                return rows

        # ---------------------------------------------
        # 데이터가 없는 경우
        # ---------------------------------------------

        return []

    except requests.exceptions.Timeout:

        st.error("⏰ NEIS 서버 응답 시간이 초과되었습니다.")

        return []

    except requests.exceptions.ConnectionError:

        st.error("🌐 NEIS 서버에 연결할 수 없습니다.")

        return []

    except requests.exceptions.RequestException:

        st.error("❌ NEIS API 요청 중 오류가 발생했습니다.")

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
    menus = re.split(
        r"<br\s*/?>",
        menu_text
    )

    result = []

    for menu in menus:

        menu = menu.strip()

        if not menu:
            continue

        # ---------------------------------------------
        # 알레르기 번호 제거
        #
        # 예:
        # 김치찌개(5.6.9)
        # ↓
        # 김치찌개
        # ---------------------------------------------

        menu = re.sub(
            r"\(\s*\d+(?:\.\d+)*\s*\)",
            "",
            menu
        )

        # 남아있는 알레르기 번호 제거
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
# 제목
# =========================================================

st.markdown(
    '<div class="title">🍚 보라고등학교 급식</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">NEIS 학교급식 정보</div>',
    unsafe_allow_html=True
)


# =========================================================
# 학교 정보
# =========================================================

st.markdown("""
<div class="school-box">

🏫 <b>보라고등학교</b>

<br><br>

경기도교육청 · 학교코드 7530882

</div>
""", unsafe_allow_html=True)


# =========================================================
# 날짜
# =========================================================

today = datetime.date.today()

selected_date = st.date_input(
    "📅 급식 날짜를 선택하세요",
    value=today,
    format="YYYY-MM-DD"
)


# =========================================================
# 오늘 급식 버튼
# =========================================================

if st.button(
    "📅 오늘 급식 보기",
    use_container_width=True
):

    selected_date = today

    # 세션 상태에 날짜 저장
    st.session_state["selected_date"] = today

    st.rerun()


# 세션 상태에 저장된 날짜가 있으면 사용
if "selected_date" in st.session_state:

    selected_date = st.session_state["selected_date"]


# =========================================================
# 날짜 정보
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
    <div class="date-box">
        {selected_date.strftime("%Y년 %m월 %d일")}
        <span style="color:#777;">
            ({day_name})
        </span>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# API 날짜 형식
# =========================================================

date_string = selected_date.strftime("%Y%m%d")


# =========================================================
# 급식 조회
# =========================================================

with st.spinner("🍚 급식 정보를 불러오는 중..."):

    meals = get_meal(date_string)


# =========================================================
# 급식 출력
# =========================================================

if not meals:

    st.info(
        "🍽️ 해당 날짜에는 등록된 급식 정보가 없습니다.\n\n"
        "주말, 공휴일, 방학 등의 경우 급식이 없을 수 있습니다."
    )

else:

    for meal in meals:

        # ---------------------------------------------
        # 중식 / 석식 / 조식
        # ---------------------------------------------

        meal_name = meal.get(
            "MMEAL_SC_NM",
            "급식"
        )

        # ---------------------------------------------
        # 메뉴
        # ---------------------------------------------

        menu_text = meal.get(
            "DDISH_NM",
            ""
        )

        # ---------------------------------------------
        # 칼로리
        # ---------------------------------------------

        calorie = meal.get(
            "CAL_INFO",
            ""
        )

        menus = clean_menu(menu_text)

        # ---------------------------------------------
        # 급식 종류 제목
        # ---------------------------------------------

        st.markdown(
            f"""
            <div class="meal-title">
                🍱 {meal_name}
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------------------------------------
        # 메뉴 박스
        # ---------------------------------------------

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

        # ---------------------------------------------
        # 칼로리 표시
        # ---------------------------------------------

        if calorie:

            calorie_html = f"""
            <div class="calorie">
                🔥 총 열량 : {calorie}
            </div>
            """

        else:

            calorie_html = """
            <div class="calorie">
                🔥 칼로리 정보 없음
            </div>
            """

        # ---------------------------------------------
        # 최종 출력
        # ---------------------------------------------

        st.markdown(
            f"""
            <div class="menu-box">

                {menu_html}

                {calorie_html}

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# 하단 안내
# =========================================================

st.markdown(
    """
    <div class="footer">

        급식 정보는 NEIS 학교급식 식단 정보를 이용합니다.<br>
        실제 급식과 일부 변경될 수 있습니다.

    </div>
    """,
    unsafe_allow_html=True
)
