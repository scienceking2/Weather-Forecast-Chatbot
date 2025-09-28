import os
import streamlit as st
import requests
from collections import defaultdict
from datetime import datetime, timedelta
import re

print(">>> 실행된 app.py 경로:", os.path.abspath(__file__))

st.title("너만을 위한 날씨 Chatbot 🤖🌤️")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ✅ 날씨 가져오는 함수
def get_weather(prompt):
    print(">>> get_weather() 호출됨")

    # 위치 가져오기
    ip_url = "http://ip-api.com/json/"
    location_res = requests.get(ip_url)
    location_data = location_res.json()
    lat = location_data["lat"]
    lon = location_data["lon"]
    city_name = location_data["city"]

    # ⚠️ 개인 OpenWeather API 키 입력
    api_key = "32de8baa9160b5258b5daa11c3556371"
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"

    response = requests.get(url)
    if response.status_code != 200:
        return f"❌ 날씨 API 요청 실패 (코드 {response.status_code})"

    data = response.json()

    weather_icon_map = {
        "맑": "☀️",
        "구름": "☁️",
        "흐림": "☁️",
        "비": "🌧️",
        "눈": "❄️",
        "천둥": "⛈️",
        "번개": "🌩️",
        "안개": "🌫️"
    }

    daily_data = defaultdict(list)
    for entry in data["list"]:
        date_txt = entry["dt_txt"].split(" ")[0]
        daily_data[date_txt].append(entry)

    today = datetime.now().date()

    # ======================
    # 🔎 날짜 해석
    # ======================
    day_offset = None
    target_dates = []
    title = ""

    if "오늘" in prompt:
        day_offset = 0
    elif "내일" in prompt:
        day_offset = 1
    elif "모레" in prompt:
        day_offset = 2
    elif "글피" in prompt:
        day_offset = 3
    else:
        match = re.search(r"(\d+)일\s*뒤", prompt)
        if match:
            day_offset = int(match.group(1))

    weekdays_map = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}
    weekday_target = None
    for k, v in weekdays_map.items():
        if k + "요일" in prompt:
            weekday_target = v
            break

    weekend = "주말" in prompt

    # ======================
    # 🔎 출력 날짜 결정
    # ======================
    if day_offset is not None:
        target_date = str(today + timedelta(days=day_offset))
        if target_date in daily_data:
            target_dates = [target_date]
            if day_offset == 0:
                title = f"📍 {city_name} 오늘 날씨"
            elif day_offset == 1:
                title = f"📍 {city_name} 내일 날씨"
            elif day_offset == 2:
                title = f"📍 {city_name} 모레 날씨"
            elif day_offset == 3:
                title = f"📍 {city_name} 글피 날씨"
            else:
                title = f"📍 {city_name} {day_offset}일 뒤({target_date}) 날씨"
        else:
            target_dates = list(daily_data.keys())[:5]
            title = f"📍 {city_name} {day_offset}일 뒤 데이터 없음 → 5일치 예보"
    elif weekday_target is not None:
        for i in range(1, 8):
            check_date = today + timedelta(days=i)
            if check_date.weekday() == weekday_target:
                target_date = str(check_date)
                if target_date in daily_data:
                    target_dates = [target_date]
                    title = f"📍 {city_name} {check_date.strftime('%A')}({target_date}) 날씨"
                break
        if not target_dates:
            target_dates = list(daily_data.keys())[:5]
            title = f"📍 {city_name} 요일 데이터 없음 → 5일치 예보"
    elif weekend:
        for i in range(1, 8):
            check_date = today + timedelta(days=i)
            if check_date.weekday() in [5, 6]:
                target_date = str(check_date)
                if target_date in daily_data:
                    target_dates.append(target_date)
        if target_dates:
            title = f"📍 {city_name} 이번 주말 날씨"
        else:
            target_dates = list(daily_data.keys())[:5]
            title = f"📍 {city_name} 주말 데이터 없음 → 5일치 예보"
    elif "5일" in prompt or "오일" in prompt:
        target_dates = list(daily_data.keys())[:5]
        title = f"📍 {city_name} 5일치 기상 예보"
    else:
        target_dates = list(daily_data.keys())[:5]
        title = f"📍 {city_name} 5일치 기상 예보"

    # ======================
    # 🔎 결과 출력 (가로 카드 레이아웃)
    # ======================
    st.markdown(f"## {title}")

    cols = st.columns(len(target_dates))  # 날짜 수만큼 열 생성

    for col, date in zip(cols, target_dates):
        entries = daily_data[date]
        temps = [e["main"]["temp"] for e in entries]
        min_temp = min(temps)
        max_temp = max(temps)

        weather = entries[0]["weather"][0]["description"]
        icon = "🌍"
        for key, val in weather_icon_map.items():
            if key in weather:
                icon = val
                break

        alert_msgs = []
        if "비" in weather:
            alert_msgs.append("☔ 우산 챙겨라!")
        if max_temp >= 35:
            alert_msgs.append("🌂 양산 챙겨라!")
        if (max_temp - min_temp) >= 15:
            alert_msgs.append("🧥 겉옷 챙겨라!")

        with col:
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:15px; border-radius:12px; margin:5px; background-color:#f9f9f9; text-align:center;">
                <div style="font-size:48px;">{icon}</div>
                <b>📅 {date}</b><br>
                <span style="font-size:18px;">{weather}</span><br>
                🌡️ <span style="color:blue;">{min_temp:.1f}°C</span> / 
                <span style="color:red;">{max_temp:.1f}°C</span><br>
                {"<br>".join(alert_msgs) if alert_msgs else ""}
            </div>
            """, unsafe_allow_html=True)

    return ""  # 이미 출력했으므로 빈 문자열 반환

# ✅ OpenRouter 챗봇 함수
def ask_openrouter(messages):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "openai/gpt-4o-mini",
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=data)
    res_json = response.json()
    if "choices" in res_json:
        return res_json["choices"][0]["message"]["content"]
    else:
        return f"❌ 오류: {res_json}"

# ✅ 기존 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ✅ 키워드
WEATHER_KEYWORDS = ["날씨", "기온", "온도", "덥", "더워", "추워", "비", "눈", "맑", "흐림", "흐려"]

# ✅ 입력 받기
if prompt := st.chat_input("무엇을 도와드릴까요?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if any(keyword in prompt for keyword in WEATHER_KEYWORDS):
        reply = get_weather(prompt)
    else:
        reply = ask_openrouter(st.session_state.messages)

    with st.chat_message("assistant"):
        if reply:
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

