import streamlit as st
import pandas as pd
import re

# 1. Настройки страницы и ГРАФИКА СОТ
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    
    /* ГЕКСАГОНАЛЬНАЯ СЕТКА */
    .honeycomb {
        display: flex; flex-wrap: wrap; justify-content: center;
        list-style: none; padding: 20px 0; margin: 0 auto; max-width: 900px;
    }
    .hex {
        width: 150px; height: 170px; background: #007bff;
        clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
        display: flex; align-items: center; justify-content: center;
        text-align: center; color: white; font-weight: bold;
        margin: 5px; transition: 0.3s; cursor: pointer; padding: 15px;
        font-size: 14px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .hex:hover { transform: scale(1.1); background: #0056b3; }
    
    /* Карточки сотрудников */
    .card {
        background: white; border-radius: 12px; padding: 15px;
        border: 1px solid #eee; text-align: center; margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .img-circle {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; border: 3px solid #f0f2f5; margin-bottom: 10px;
    }
    
    /* Кнопка микрофона БЕЗ ПОЛОС */
    .mic-button {
        position: fixed; bottom: 30px; right: 30px;
        width: 60px; height: 60px; background: #ff4b4b;
        border-radius: 50%; display: flex; align-items: center;
        justify-content: center; color: white; cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ФУНКЦИИ
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

# 3. ЛОГИКА ПРИЛОЖЕНИЯ
try:
    df = load_data()
    
    if 'page' not in st.session_state:
        st.session_state.page = "home"

    # ГЛАВНЫЙ ЭКРАН - УЛЕЙ
    if st.session_state.page == "home":
        st.markdown("<h1 style='text-align: center;'>Справочник КЛМ</h1>", unsafe_allow_html=True)
        
        # Рисуем соты как кнопки, но стилизуем их
        depts = {
            "Администрация": 1, "Отдел ВЭД": 2, "Ветпрепараты": 3,
            "Агропродукты": 4, "Сырье и корма": 5, "Кадры / Право": 6,
            "Финансы": 7, "Хоз. служба": 8
        }
        
        st.write("### Выберите отдел:")
        
        # Создаем сетку сот
        cols = st.columns(4)
        for i, (name, d_id) in enumerate(depts.items()):
            with cols[i % 4]:
                # Используем стандартную кнопку, которую CSS превратит в соту (частично)
                if st.button(name, key=f"d_{d_id}", use_container_width=True):
                    st.session_state.page = d_id
                    st.rerun()

        if st.button("👥 Показать всех сотрудников", use_container_width=True):
            st.session_state.page = 0
            st.rerun()

    # ЭКРАН СОТРУДНИКОВ
    else:
        if st.button("← Вернуться к сотам"):
            st.session_state.page = "home"
            st.rerun()

        current_id = st.session_state.page
        f_df = df if current_id == 0 else df[df['d_id'] == current_id]
        
        search = st.text_input("🔍 Поиск по фамилии", "")
        if search:
            f_df = f_df[f_df['Ф.И.О.'].str.lower().str.contains(search.lower())]

        if f_df.empty:
            st.warning("Никого не нашли. Попробуйте другой запрос.")
        else:
            for i in range(0, len(f_df), 4):
                cols = st.columns(4)
                batch = f_df.iloc[i:i+4]
                for j, (_, emp) in enumerate(batch.iterrows()):
                    with cols[j]:
                        st.markdown(f"""
                        <div class="card">
                            <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                            <div style="font-weight:bold; height:40px;">{emp.get('Ф.И.О.', '---')}</div>
                            <div style="font-size:11px; color:gray; margin-bottom:10px; height:30px;">{emp.get('Должность', '-')}</div>
                            <a href="tel:{emp.get('Тел. Личный')}" style="display:block; background:#007bff; color:white; padding:8px; border-radius:6px; text-decoration:none;">📞 Позвонить</a>
                        </div>
                        """, unsafe_allow_html=True)

    # 4. МИКРОФОН (Простой JS без полос)
    st.components.v1.html("""
        <script>
        function listen() {
            const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            rec.lang = 'ru-RU';
            rec.start();
            rec.onresult = (e) => {
                alert("Джемка услышала: " + e.results[0][0].transcript);
            };
        }
        </script>
        <div style="position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; background: #ff4b4b; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; color: white; font-size: 30px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);" onclick="listen()">🎤</div>
    """, height=80)

except Exception as e:
    st.error(f"Ошибка: {e}")
