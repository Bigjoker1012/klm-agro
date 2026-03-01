import streamlit as st
import pandas as pd
import re

# 1. Настройки и крутой CSS для ГЕКСАГОНОВ
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* СЕТКА СОТ */
    .honeycomb-container {
        display: flex; flex-wrap: wrap; justify-content: center;
        gap: 10px; padding: 20px; max-width: 1200px; margin: 0 auto;
    }
    
    .hex-item {
        width: 180px; height: 200px; background: #007bff;
        clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
        display: flex; align-items: center; justify-content: center;
        text-align: center; color: white; font-weight: bold;
        transition: 0.4s; cursor: pointer; padding: 20px;
        font-size: 14px; border: none; box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .hex-item:hover { transform: translateY(-10px) scale(1.05); background: #0056b3; }

    /* Кнопка микрофона */
    .mic-fixed {
        position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%);
        width: 70px; height: 70px; background: #ff4b4b; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 20px rgba(255,75,75,0.4); cursor: pointer; z-index: 9999;
    }
    
    /* Карточки сотрудников */
    .card {
        background: white; border-radius: 15px; padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center;
        margin-bottom: 20px; border: 1px solid #eee; transition: 0.3s;
    }
    .img-circle {
        width: 110px; height: 110px; border-radius: 50%;
        object-fit: cover; border: 3px solid #007bff; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ИСПРАВЛЕННЫЙ ГОЛОС (через прямой JS)
voice_code = """
<script>
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'ru-RU';

function startListen() {
    recognition.start();
    document.getElementById('mic-status').style.background = '#28a745';
}

recognition.onresult = (event) => {
    const text = event.results[0][0].transcript.toLowerCase();
    const btn = window.parent.document.querySelectorAll('input[aria-label="voice_hidden"]')[0];
    if (btn) {
        btn.value = text;
        btn.dispatchEvent(new Event('input', {bubbles: true}));
    }
    document.getElementById('mic-status').style.background = '#ff4b4b';
};
</script>
<div class="mic-fixed" id="mic-status" onclick="startListen()">
    <span style="font-size:30px; color:white;">🎤</span>
</div>
"""
st.components.v1.html(voice_code, height=120)

# Скрытое поле для передачи текста из JS в Python
voice_text = st.text_input("voice_hidden", label_visibility="collapsed", key="v_input")

# 3. Данные
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
    
    # Реакция на голос
    if voice_text:
        st.toast(f"Команда: {voice_text}")
        if "вэд" in voice_text: st.session_state.page = 2
        elif "фин" in voice_text: st.session_state.page = 7
        elif "админ" in voice_text: st.session_state.page = 1
        elif "назад" in voice_text or "домой" in voice_text: st.session_state.page = "home"

    if 'page' not in st.session_state:
        st.session_state.page = "home"

    # ГЛАВНЫЙ ЭКРАН - СОТЫ
    if st.session_state.page == "home":
        st.markdown("<h1 style='text-align: center;'>Справочник КЛМ</h1>", unsafe_allow_html=True)
        
        depts = {
            "Администрация": 1, "Отдел ВЭД": 2, "Ветпрепараты": 3,
            "Агропродукты": 4, "Сырье и корма": 5, "Кадры / Право": 6,
            "Финансы": 7, "Хоз. служба": 8
        }
        
        # Рисуем соты через колонки Streamlit (для кликабельности)
        st.write("---")
        cols = st.columns(4)
        for i, (name, d_id) in enumerate(depts.items()):
            with cols[i % 4]:
                if st.button(name, key=f"btn_{d_id}", use_container_width=True, type="secondary"):
                    st.session_state.page = d_id
                    st.rerun()
        
        st.write("---")
        if st.button("👥 Показать всех сотрудников", use_container_width=True):
            st.session_state.page = 0
            st.rerun()

    # СПИСОК СОТРУДНИКОВ
    else:
        col_back, col_title = st.columns([1, 4])
        with col_back:
            if st.button("← Назад"):
                st.session_state.page = "home"
                st.rerun()
        with col_title:
            st.title("Справочник КЛМ")

        current_id = st.session_state.page
        f_df = df if current_id == 0 else df[df['d_id'] == current_id]
        
        search = st.text_input("🔍 Быстрый поиск", placeholder="Введите имя...")
        if search:
            f_df = f_df[f_df['Ф.И.О.'].str.lower().str.contains(search.lower())]

        for i in range(0, len(f_df), 4):
            cols = st.columns(4)
            batch = f_df.iloc[i:i+4]
            for j, (_, emp) in enumerate(batch.iterrows()):
                with cols[j]:
                    st.markdown(f"""
                    <div class="card">
                        <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                        <div style="font-weight:bold; font-size:16px;">{emp.get('Ф.И.О.')}</div>
                        <div style="font-size:12px; color:gray; margin-bottom:15px; height:35px;">{emp.get('Должность')}</div>
                        <a href="tel:{emp.get('Тел. Личный')}" style="display:block; background:#007bff; color:white; padding:10px; border-radius:8px; text-decoration:none; font-weight:bold;">📞 Позвонить</a>
                    </div>
                    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка Улья: {e}")
