import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Справочник КЛМ", layout="wide")

# ЖЕСТКИЙ CSS ДЛЯ ЦВЕТОВ И КНОПОК
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Стилизация кнопок отделов (Градиенты) */
    div.stButton > button {
        height: 100px !important; border-radius: 15px !important;
        font-weight: bold !important; font-size: 18px !important;
        color: white !important; border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
    }
    /* Индивидуальная раскраска */
    div.stButton:nth-of-type(1) > button { background: linear-gradient(135deg, #2c3e50, #4ca1af) !important; }
    div.stButton:nth-of-type(2) > button { background: linear-gradient(135deg, #11998e, #38ef7d) !important; }
    div.stButton:nth-of-type(3) > button { background: linear-gradient(135deg, #ff9966, #ff5e62) !important; }
    div.stButton:nth-of-type(4) > button { background: linear-gradient(135deg, #56ab2f, #a8e063) !important; }
    div.stButton:nth-of-type(5) > button { background: linear-gradient(135deg, #4b6cb7, #182848) !important; }
    div.stButton:nth-of-type(6) > button { background: linear-gradient(135deg, #00b4db, #0083b0) !important; }
    div.stButton:nth-of-type(7) > button { background: linear-gradient(135deg, #f2994a, #f2c94c) !important; }
    div.stButton:nth-of-type(8) > button { background: linear-gradient(135deg, #8e44ad, #c0392b) !important; }

    /* Карточки и кнопки связи */
    .card {
        background: white; border-radius: 15px; padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
        margin-bottom: 20px; border: 1px solid #e1e4e8; min-height: 440px;
    }
    .img-circle {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; margin: 0 auto 10px auto; border: 2px solid #007bff;
    }
    .comm-btn {
        display: block; width: 100%; padding: 8px 0; margin-top: 5px;
        border-radius: 8px; font-size: 13px; font-weight: 600;
        text-decoration: none !important; color: white !important;
    }
    .b-call { background-color: #007bff; }
    .b-wa { background-color: #28a745; }
    .b-tg { background-color: #0088cc; }
    .b-mail { background-color: #6c757d; }
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

    st.markdown("<h2 style='text-align: center;'>Справочник КЛМ</h2>", unsafe_allow_html=True)

    # ПОИСК
    search_query = st.text_input("🔍 Поиск сотрудника", placeholder="Кого ищем?", key="search_input")

    if search_query:
        f_df = df[df['Ф.И.О.'].str.lower().str.contains(search_query.lower(), na=False) | 
                  df['Должность'].str.lower().str.contains(search_query.lower(), na=False)]
        
        if not f_df.empty:
            cols = st.columns(4)
            for i, (_, emp) in enumerate(f_df.iterrows()):
                with cols[i % 4]:
                    # Логика приоритета телефона
                    w_p, l_p = str(emp.get('Тел. Рабочий', '')), str(emp.get('Тел. Личный', ''))
                    final_p = w_p if w_p not in ["nan", ""] else l_p
                    clean_p = "".join(filter(str.isdigit, final_p))
                    mail = str(emp.get('E-mail', '')).strip()
                    
                    btns = f'<a href="tel:+{clean_p}" class="comm-btn b-call">📞 Позвонить</a>'
                    if len(clean_p) > 5:
                        btns += f'<a href="https://wa.me/{clean_p}" class="comm-btn b-wa" target="_blank">💬 WhatsApp</a>'
                        btns += f'<a href="https://t.me/+{clean_p}" class="comm-btn b-tg" target="_blank">✈️ Telegram</a>'
                    if mail != "nan" and mail != "":
                        btns += f'<a href="mailto:{mail}" class="comm-btn b-mail">✉️ Почта</a>'

                    st.markdown(f'<div class="card"><img src="{get_photo(emp.get("Фото"))}" class="img-circle"><div style="font-weight:bold;min-height:45px;">{emp.get("Ф.И.О.")}</div><div style="font-size:12px;color:gray;min-height:35px;">{emp.get("Должность")}</div>{btns}</div>', unsafe_allow_html=True)
        
        if st.button("✖ Сбросить поиск", key="reset"): st.rerun()

    # ГЛАВНЫЙ ЭКРАН
    elif st.session_state.page == "home":
        st.write("### Выберите подразделение:")
        depts = [("Администрация", 1), ("Отдел ВЭД", 2), ("Ветпрепараты", 3), ("Агропродукты", 4),
                 ("Сырье и корма", 5), ("Кадры / Право", 6), ("Финансы", 7), ("Хоз. служба", 8)]
        for r in range(0, 8, 4):
            cols = st.columns(4)
            for i, (name, d_id) in enumerate(depts[r:r+4]):
                with cols[i]:
                    if st.button(name, key=f"d_{d_id}", use_container_width=True):
                        st.session_state.page = d_id
                        st.rerun()

    # СПИСОК ОТДЕЛА
    else:
        if st.button("← Назад к отделам", key="back_up", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

        f_df = df[df['d_id'] == st.session_state.page]
        cols = st.columns(4)
        for i, (_, emp) in enumerate(f_df.iterrows()):
            with cols[i % 4]:
                w_p, l_p = str(emp.get('Тел. Рабочий', '')), str(emp.get('Тел. Личный', ''))
                phone = w_p if w_p not in ["nan", ""] else l_p
                clean_p = "".join(filter(str.isdigit, phone))
                mail = str(emp.get('E-mail', '')).strip()
                
                btns = f'<a href="tel:+{clean_p}" class="comm-btn b-call">📞 Позвонить</a>'
                if len(clean_p) > 5:
                    btns += f'<a href="https://wa.me/{clean_p}" class="comm-btn b-wa" target="_blank">💬 WhatsApp</a>'
                    btns += f'<a href="https://t.me/+{clean_p}" class="comm-btn b-tg" target="_blank">✈️ Telegram</a>'
                if mail != "nan" and mail != "":
                    btns += f'<a href="mailto:{mail}" class="comm-btn b-mail">✉️ Почта</a>'

                st.markdown(f'<div class="card"><img src="{get_photo(emp.get("Фото"))}" class="img-circle"><div style="font-weight:bold;min-height:45px;">{emp.get("Ф.И.О.")}</div><div style="font-size:12px;color:gray;min-height:35px;">{emp.get("Должность")}</div>{btns}</div>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("← Вернуться к сотам", key="back_down", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

except Exception as e:
    st.error(f"Упс: {e}")
