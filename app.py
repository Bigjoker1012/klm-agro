import streamlit as st
import pandas as pd
import re

# 1. Настройка страницы
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

# CSS для настоящих цветных кликабельных плиток
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Стилизация КНОПОК-СОТ */
    div.stButton > button {
        display: flex; align-items: center; justify-content: center;
        height: 100px !important; border-radius: 15px !important;
        color: white !important; font-weight: bold !important; font-size: 18px !important;
        border: none !important; transition: 0.3s !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        margin-bottom: 10px !important;
    }
    div.stButton > button:hover { transform: scale(1.03); filter: brightness(1.1); }
    
    /* Индивидуальные цвета для кнопок (по порядку) */
    /* Администрация */
    div[data-testid="stSidebarNav"] + div div.stButton:nth-of-type(1) button, 
    div.stButton:nth-child(1) > button { background: linear-gradient(135deg, #1e3c72, #2a5298) !important; }
    
    /* Принудительно задаем цвета через ключи, чтобы не путались */
    .st-key-d_1 > button { background: linear-gradient(135deg, #2c3e50, #4ca1af) !important; }
    .st-key-d_2 > button { background: linear-gradient(135deg, #11998e, #38ef7d) !important; }
    .st-key-d_3 > button { background: linear-gradient(135deg, #ff9966, #ff5e62) !important; }
    .st-key-d_4 > button { background: linear-gradient(135deg, #56ab2f, #a8e063) !important; }
    .st-key-d_5 > button { background: linear-gradient(135deg, #4b6cb7, #182848) !important; }
    .st-key-d_6 > button { background: linear-gradient(135deg, #00b4db, #0083b0) !important; }
    .st-key-d_7 > button { background: linear-gradient(135deg, #f2994a, #f2c94c) !important; }
    .st-key-d_8 > button { background: linear-gradient(135deg, #8e44ad, #c0392b) !important; }

    /* Карточки сотрудников */
    .card {
        background: white; border-radius: 15px; padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
        margin-bottom: 20px; border: 1px solid #e1e4e8; min-height: 400px;
    }
    .img-circle {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; margin: 0 auto 10px auto; border: 3px solid #eee;
    }
    .btn-comm {
        display: block; width: 100%; padding: 10px 0; margin-top: 5px;
        border-radius: 8px; font-size: 13px; font-weight: 600;
        text-decoration: none !important; color: white !important;
    }
    .b-call { background-color: #007bff; }
    .b-wa { background-color: #28a745; }
    .b-tg { background-color: #0088cc; }
    </style>
    """, unsafe_allow_html=True)

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
    
    # Состояния
    if 'page' not in st.session_state: st.session_state.page = "home"

    st.markdown("<h2 style='text-align: center;'>Справочник КЛМ</h2>", unsafe_allow_html=True)

    # 2. ЛОГИКА ПОИСКА (Работает независимо)
    search_query = st.text_input("🔍 Найти сотрудника...", placeholder="Фамилия или должность", key="search_main")

    if search_query:
        f_df = df[df['Ф.И.О.'].str.lower().str.contains(search_query.lower()) | 
                  df['Должность'].str.lower().str.contains(search_query.lower())]
        
        if not f_df.empty:
            cols = st.columns(4)
            for i, (_, emp) in enumerate(f_df.iterrows()):
                with cols[i % 4]:
                    p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                    phone = "".join(filter(str.isdigit, str(p_val)))
                    st.markdown(f'<div class="card"><img src="{get_photo(emp.get("Фото"))}" class="img-circle"><div style="font-weight:bold;height:45px;">{emp.get("Ф.И.О.")}</div><div style="font-size:12px;color:gray;height:40px;">{emp.get("Должность")}</div><a href="tel:+{phone}" class="btn-comm b-call">📞 Позвонить</a></div>', unsafe_allow_html=True)
        
        if st.button("✖ Сбросить поиск"):
            st.rerun()

    # 3. ГЛАВНЫЙ ЭКРАН (ЦВЕТНЫЕ СОТЫ)
    elif st.session_state.page == "home":
        depts = [
            ("🏢 Администрация", 1), ("🌍 Отдел ВЭД", 2), ("💊 Ветпрепараты", 3), ("🚜 Агропродукты", 4),
            ("🌾 Сырье и корма", 5), ("⚖️ Кадры / Право", 6), ("💰 Финансы", 7), ("🛠️ Хоз. служба", 8)
        ]
        
        # Рисуем сетку 2 ряда по 4 колонки
        for r in range(0, 8, 4):
            cols = st.columns(4)
            for i, (name, d_id) in enumerate(depts[r:r+4]):
                with cols[i]:
                    if st.button(name, key=f"d_{d_id}", use_container_width=True):
                        st.session_state.page = d_id
                        st.rerun()

    # 4. СТРАНИЦА ОТДЕЛА
    else:
        if st.button("← Назад к отделам", key="back_btn"):
            st.session_state.page = "home"
            st.rerun()

        f_df = df[df['d_id'] == st.session_state.page]
        cols = st.columns(4)
        for i, (_, emp) in enumerate(f_df.iterrows()):
            with cols[i % 4]:
                p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                phone = "".join(filter(str.isdigit, str(p_val)))
                
                btns = f'<a href="tel:+{phone}" class="btn-comm b-call">📞 Позвонить</a>'
                if len(phone) > 5:
                    btns += f'<a href="https://wa.me/{phone}" class="btn-comm b-wa" target="_blank">💬 WhatsApp</a>'
                    btns += f'<a href="https://t.me/+{phone}" class="btn-comm b-tg" target="_blank">✈️ Telegram</a>'
                
                st.markdown(f"""
                <div class="card">
                    <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                    <div style="font-weight:bold; height:40px;">{emp.get('Ф.И.О.')}</div>
                    <div style="font-size:11px; color:gray; height:35px;">{emp.get('Должность')}</div>
                    {btns}
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Системная ошибка: {e}")
