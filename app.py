import streamlit as st
import pandas as pd
import re

# 1. Настройка страницы
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

# Улучшенный CSS: индивидуальные цвета и фиксированные стили
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Стилизация КНОПОК-СОТ с привязкой к тексту (чтобы не были только синими) */
    div.stButton > button {
        height: 100px !important; border-radius: 15px !important;
        color: white !important; font-weight: bold !important; font-size: 18px !important;
        border: none !important; transition: 0.3s !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }
    
    /* Красим по конкретным отделам */
    div.stButton > button:contains("Администрация") { background: linear-gradient(135deg, #2c3e50, #4ca1af) !important; }
    div.stButton > button:contains("ВЭД") { background: linear-gradient(135deg, #11998e, #38ef7d) !important; }
    div.stButton > button:contains("Ветпрепараты") { background: linear-gradient(135deg, #ff9966, #ff5e62) !important; }
    div.stButton > button:contains("Агропродукты") { background: linear-gradient(135deg, #56ab2f, #a8e063) !important; }
    div.stButton > button:contains("Сырье") { background: linear-gradient(135deg, #4b6cb7, #182848) !important; }
    div.stButton > button:contains("Кадры") { background: linear-gradient(135deg, #00b4db, #0083b0) !important; }
    div.stButton > button:contains("Финансы") { background: linear-gradient(135deg, #f2994a, #f2c94c) !important; }
    div.stButton > button:contains("Хоз. служба") { background: linear-gradient(135deg, #8e44ad, #c0392b) !important; }

    /* Кнопка НАЗАД (белая с рамкой) */
    .st-key-back_top > button, .st-key-back_bot > button {
        background: white !important; color: #333 !important; border: 1px solid #ccc !important; height: 50px !important;
    }

    .card {
        background: white; border-radius: 15px; padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
        margin-bottom: 20px; border: 1px solid #e1e4e8; min-height: 420px;
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
    if 'page' not in st.session_state: st.session_state.page = "home"

    st.markdown("<h2 style='text-align: center;'>Справочник КЛМ</h2>", unsafe_allow_html=True)

    # ПОИСК
    search_query = st.text_input("🔍 Поиск...", placeholder="Кого ищем?", key="search_main")

    if search_query:
        # Логика поиска
        f_df = df[df['Ф.И.О.'].str.lower().str.contains(search_query.lower(), na=False) | 
                  df['Должность'].str.lower().str.contains(search_query.lower(), na=False)]
        
        if not f_df.empty:
            cols = st.columns(4)
            for i, (_, emp) in enumerate(f_df.iterrows()):
                with cols[i % 4]:
                    # ПРИОРИТЕТ ТЕЛЕФОНА: Рабочий -> Личный
                    p_val = emp.get('Тел. Рабочий') if pd.notnull(emp.get('Тел. Рабочий')) and str(emp.get('Тел. Рабочий')).strip() != "" else emp.get('Тел. Личный')
                    phone = "".join(filter(str.isdigit, str(p_val)))
                    st.markdown(f'<div class="card"><img src="{get_photo(emp.get("Фото"))}" class="img-circle"><div style="font-weight:bold;height:45px;">{emp.get("Ф.И.О.")}</div><div style="font-size:12px;color:gray;height:40px;">{emp.get("Должность")}</div><a href="tel:+{phone}" class="btn-comm b-call">📞 Позвонить</a></div>', unsafe_allow_html=True)
        
        if st.button("✖ Вернуться к отделам", key="reset_search"):
            st.rerun()

    # ГЛАВНЫЙ ЭКРАН
    elif st.session_state.page == "home":
        depts = [
            ("🏢 Администрация", 1), ("🌍 Отдел ВЭД", 2), ("💊 Ветпрепараты", 3), ("🚜 Агропродукты", 4),
            ("🌾 Сырье и корма", 5), ("⚖️ Кадры / Право", 6), ("💰 Финансы", 7), ("🛠️ Хоз. служба", 8)
        ]
        for r in range(0, 8, 4):
            cols = st.columns(4)
            for i, (name, d_id) in enumerate(depts[r:r+4]):
                with cols[i]:
                    if st.button(name, key=f"d_{d_id}", use_container_width=True):
                        st.session_state.page = d_id
                        st.rerun()

    # СТРАНИЦА ОТДЕЛА
    else:
        # Кнопка НАЗАД СВЕРХУ
        if st.button("← Назад к сотам", key="back_top"):
            st.session_state.page = "home"
            st.rerun()

        f_df = df[df['d_id'] == st.session_state.page]
        cols = st.columns(4)
        for i, (_, emp) in enumerate(f_df.iterrows()):
            with cols[i % 4]:
                # ЛОГИКА ТЕЛЕФОНОВ: Только рабочий, если он есть
                work_p = emp.get('Тел. Рабочий')
                priv_p = emp.get('Тел. Личный')
                
                final_p = work_p if pd.notnull(work_p) and str(work_p).strip() != "" else priv_p
                phone = "".join(filter(str.isdigit, str(final_p)))
                
                btns = f'<a href="tel:+{phone}" class="btn-comm b-call">📞 Позвонить</a>'
                if len(phone) > 5:
                    btns += f'<a href="https://wa.me/{phone}" class="btn-comm b-wa" target="_blank">💬 WhatsApp</a>'
                    btns += f'<a href="https://t.me/+{phone}" class="btn-comm b-tg" target="_blank">✈️ Telegram</a>'
                
                st.markdown(f'<div class="card"><img src="{get_photo(emp.get("Фото"))}" class="img-circle"><div style="font-weight:bold;height:40px;">{emp.get("Ф.И.О.")}</div><div style="font-size:11px;color:gray;height:35px;">{emp.get("Должность")}</div>{btns}</div>', unsafe_allow_html=True)

        # Кнопка НАЗАД СНИЗУ (для удобства листания)
        st.write("---")
        if st.button("← Назад к сотам", key="back_bot", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

except Exception as e:
    st.error(f"Ошибка: {e}")
