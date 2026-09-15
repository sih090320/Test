import streamlit as st
from openai import OpenAI

st.title("✨ 칭찬 생성기")
st.write("칭찬받고 싶은 내용을 입력하면 AI가 멋진 칭찬을 해줍니다!")

# Streamlit Secrets에서 API 키 불러오기
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API 키가 설정되지 않았습니다. Secrets를 확인해주세요.")
    st.stop()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# 사용자 입력 받기
user_input = st.text_input("오늘 어떤 일을 했나요?", placeholder="예: 오늘 아침 일찍 일어나서 운동을 했어.")

if st.button("칭찬 받기"):
    if user_input.strip() == "":
        st.warning("내용을 입력해주세요!")
    else:
        with st.spinner("칭찬을 생성하는 중입니다..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-5.4-nano",
                    messages=[
                        {"role": "system", "content": "너는 다정하고 따뜻한 칭찬 전문가야. 사용자의 이야기에 맞춰 진심 어린 칭찬을 해줘."},
                        {"role": "user", "content": user_input}
                    ]
                )
                
                # 결과 출력
                result = response.choices[0].message.content
                st.success("🎉 칭찬 메시지")
                st.write(result)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
