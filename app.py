import streamlit as st
import pandas as pd
import re

# 1. Настройки страницы и стили СОТ
st.set_page_config(page_title="КЛМ Справочник", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    
    /* Контейнер для сот */
    .honeycomb {
        display: flex; flex-wrap: wrap; justify-content: center;
        max-width: 1000px; margin: 0 auto; padding-top: 50px;
    }
    
    /* Сама сота (отдел) */
    .hex {
        width: 150px; height: 170px; background: #007bff;
        clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
        display: flex; align-items: center; justify-content: center;
        text-align: center; color: white; font-weight: bold;
        margin: 5px; transition: 0.3s; cursor: pointer;
        padding: 15px; font-size: 14px; line-height: 1.2;
    }
    .hex:hover { transform: scale(1.1); background: #0056b3; z-index: 10; }
    
    /* Кнопка микрофона */
    .mic-container {
        position: fixed; bottom: 30px; right: 30px; z-index: 1000;
    }
    .mic-btn {
        width: 70px; height: 70px; background: #ff4b4b; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); cursor: pointer; border: none;
    }
    
    /* Карточки сотрудников (адаптив) */
    .card {
        background: white; border-radius: 15px; padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;
        margin-bottom: 20px; border: 1px solid #eee;
    }
    .img-circle {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; margin-bottom: 10px; border: 3px solid #f0f2f5;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Голосовой движок (JavaScript)
st.components.v1.html("""
    <script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'ru-RU';
    recognition.continuous = false;

    function startListening() {
        const btn = document.getElementById('mic-icon');
        btn.style.background = '#28a745';
        recognition.start();
    }

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript.toLowerCase();
        window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'voice_input', value: text}, '*');
        document.getElementById('mic-icon').style.background = '#ff4b4b';
    };
    
    recognition.onerror = () => {
        document.getElementById('mic-icon').style.background = '#ff4b4b';
    };
    </script>
    <div class="mic-container">
        <button class="mic-btn" id="mic-icon" onclick="startListening()">🎤</button>
    </div>
""", height=100)

# Прием данных из голоса
if 'voice_input' not in st.session_state:
    st.session_state.voice_input = ""

# 3. Загрузка данных
@st.cache_data(ttl=600)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"
    df = pd.read_csv(url)
    df.columns = [str(c).strip() for c in df.columns]
    if 'ID отдела' in df.columns:
        df['d_id'] = pd.to_numeric(df['ID отдела'], errors='coerce').fillna(0).astype(int)
    return df

def get_photo(url):
    placeholder = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    if pd.isna(url) or str(url).strip() == "": return placeholder
    match = re.search(r'[-\w]{25,}', str(url))
    return f"https://lh3.googleusercontent.com/d/{match.group()}" if match else placeholder

try:
    df = load_data()
    
    # Обработка голоса (Джемка слушает)
    cmd = st.session_state.voice_input
    if cmd:
        st.info(f"Слышу команду: {cmd}")
        # Логика поиска по голосу (примеры)
        if "вэд" in cmd: st.session_state.page = 2
        elif "админ" in cmd: st.session_state.page = 1
        elif "все" in cmd: st.session_state.page = 0
        st.session_state.voice_input = "" # Сброс

    # Навигация
    if 'page' not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "home":
        st.title("🧬 Структура КЛМ (Улей)")
        depts = {
            "001 Администрация": 1, "002 Отдел ВЭД": 2, "003 Ветпрепараты": 3,
            "004 Агропродукты": 4, "005 Сырье и корма": 5, "006 Кадры / Право": 6,
            "007 Финансы": 7, "008 Хоз. служба": 8
        }
        
        st.write("### Выберите отдел или используйте микрофон 🎤")
        
        # Отрисовка сот кнопками
        cols = st.columns(4)
        for i, (name, d_id) in enumerate(depts.items()):
            with cols[i % 4]:
                if st.button(name, use_container_width=True):
                    st.session_state.page = d_id
        
        if st.button("👥 Показать всех сотрудников", type="primary"):
            st.session_state.page = 0

    else:
        # Экран отдела/сотрудников
        if st.button("← Назад в Улей"):
            st.session_state.page = "home"
            st.rerun()

        current_id = st.session_state.page
        f_df = df if current_id == 0 else df[df['d_id'] == current_id]
        
        st.subheader(f"Сотрудники ({len(f_df)})")
        
        search = st.text_input("🔍 Быстрый поиск", "")
        if search:
            f_df = f_df[f_df['Ф.И.О.'].str.lower().str.contains(search.lower())]

        # Сетка карточек
        for i in range(0, len(f_df), 4):
            cols = st.columns(4)
            batch = f_df.iloc[i:i+4]
            for j, (_, emp) in enumerate(batch.iterrows()):
                with cols[j]:
                    st.markdown(f"""
                    <div class="card">
                        <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                        <div style="font-weight:bold; height:40px;">{emp.get('Ф.И.О.')}</div>
                        <div style="font-size:12px; color:gray; margin-bottom:10px;">{emp.get('Должность')}</div>
                        <a href="tel:{emp.get('Тел. Личный')}" style="display:block; background:#007bff; color:white; padding:8px; border-radius:5px; text-decoration:none; margin-bottom:5px;">📞 Звонок</a>
                    </div>
                    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Улей временно недоступен: {e}")
