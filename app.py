import streamlit as st
import pandas as pd
import re

# 1. Настройка страницы
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

# 2. Жёсткий CSS для раскраски кнопок
st.markdown("""
    <style>
    /* Фон приложения */
    .stApp { background-color: #f8f9fa; }
    
    /* Общий стиль для всех кнопок отделов */
    div.stButton > button {
        height: 100px !important;
        border-radius: 15px !important;
        font-weight: bold !important;
        font-size: 20px !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
        margin-bottom: 10px !important;
    }

    /* Раскрашиваем каждую кнопку по очереди (nth-of-type) */
    /* Важно: считаем только кнопки отделов в сетке */
    div.stButton:nth-of-type(1) > button { background: linear-gradient(135deg, #2c3e50, #4ca1af) !important; }
    div.stButton:nth-of-type(2) > button { background: linear-gradient(135deg, #11998e, #38ef7d) !important; }
    div.stButton:nth-of-type(3) > button { background: linear-gradient(135deg, #ff9966, #ff5e62) !important; }
    div.stButton:nth-of-type(4) > button { background: linear-gradient(135deg, #56ab2f, #a8e063) !important; }
    div.stButton:nth-of-type(5) > button { background: linear-gradient(135deg, #4b6cb7, #182848) !important; }
    div.stButton:nth-of-type(6) > button { background: linear-gradient(135deg, #00b4db, #0083b0) !important; }
    div.stButton:nth-of-type(7) > button { background: linear-gradient(135deg, #f2994a, #f2c94c) !important; }
    div.stButton:nth-of-type(8) > button { background: linear-gradient(135deg, #8e44ad, #c0392b) !important; }

    /* Кнопки возврата и сброса (делаем их скромнее) */
    .st-key-back_up > button, .st-key-back_down > button, .st-key-reset_btn > button {
        background: #f1f2f6 !important;
        color: #2f3542 !important;
        height: 50px !important;
        font-size: 16px !important;
    }

    /* Карточки сотрудников */
    .emp-card {
        background: white; border-radius: 15px; padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); text-align: center;
        border: 1px solid #eee; margin-bottom: 20px;
    }
    .img-circle {
        width: 110px; height: 110px; border-radius: 50%;
        object-fit: cover; margin-bottom: 15px; border: 3px solid #f0f0f0;
    }
    .call-btn {
        background-color: #007bff; color: white !important;
        display: block; width: 100%; padding: 12px;
        border-radius: 10px; font-weight: bold; text-decoration: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
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
    if 'page' not in st.session_state: st.session_state.page = "home"

    st.markdown("<h1 style='text-align: center;'>Справочник КЛМ</h1>", unsafe_allow_html=True)

    # 1. ПОИСК
    search_q = st.text_input("🔍 Поиск сотрудника", placeholder="Начните вводить фамилию...", key="search_input")

    if search_q:
        results = df[df['Ф.И.О.'].str.lower().str.contains(search_q.lower(), na=False) | 
                     df['Должность'].str.lower().str.contains(search_q.lower(), na=False)]
        
        if not results.empty:
            cols = st.columns(4)
            for i, (_, emp) in enumerate(results.iterrows()):
                with cols[i % 4]:
                    # Логика приоритета рабочего телефона
                    work_phone = str(emp.get('Тел. Рабочий', '')).strip()
                    priv_phone = str(emp.get('Тел. Личный', '')).strip()
                    final_phone = work_phone if work_phone not in ["nan", ""] else priv_phone
                    clean_phone = "".join(filter(str.isdigit, final_phone))
                    
                    st.markdown(f"""
                        <div class="emp-card">
                            <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                            <div style="font-weight:bold; font-size:16px;">{emp.get('Ф.И.О.')}</div>
                            <div style="color:gray; font-size:13px; margin-bottom:15px;">{emp.get('Должность')}</div>
                            <a href="tel:+{clean_phone}" class="call-btn">📞 Позвонить</a>
                        </div>
                    """, unsafe_allow_html=True)
        
        if st.button("✖ Сбросить поиск", key="reset_btn", use_container_width=True):
            st.rerun()

    # 2. ГЛАВНЫЙ ЭКРАН (ТОЛЬКО КНОПКИ)
    elif st.session_state.page == "home":
        st.markdown("### Выберите отдел:")
        depts = [
            ("Администрация", 1), ("Отдел ВЭД", 2), ("Ветпрепараты", 3), ("Агропродукты", 4),
            ("Сырье и корма", 5), ("Кадры / Право", 6), ("Финансы", 7), ("Хоз. служба", 8)
        ]
        
        # Сетка 2 ряда по 4 кнопки
        for r in range(0, 8, 4):
            cols = st.columns(4)
            for i, (name, d_id) in enumerate(depts[r:r+4]):
                with cols[i]:
                    if st.button(name, key=f"d_{d_id}", use_container_width=True):
                        st.session_state.page = d_id
                        st.rerun()

    # 3. СПИСОК ОТДЕЛА
    else:
        if st.button("← Назад к отделам", key="back_up", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

        dept_df = df[df['d_id'] == st.session_state.page]
        cols = st.columns(4)
        for i, (_, emp) in enumerate(dept_df.iterrows()):
            with cols[i % 4]:
                work_p = str(emp.get('Тел. Рабочий', '')).strip()
                priv_p = str(emp.get('Тел. Личный', '')).strip()
                phone = work_p if work_p not in ["nan", ""] else priv_p
                clean_p = "".join(filter(str.isdigit, phone))
                
                st.markdown(f"""
                    <div class="emp-card">
                        <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                        <div style="font-weight:bold;">{emp.get('Ф.И.О.')}</div>
                        <div style="color:gray; font-size:12px; margin-bottom:10px;">{emp.get('Должность')}</div>
                        <a href="tel:+{clean_p}" class="call-btn">📞 Позвонить</a>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("← Вернуться к выбору отдела", key="back_down", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

except Exception as e:
    st.error(f"Ошибка: {e}")
