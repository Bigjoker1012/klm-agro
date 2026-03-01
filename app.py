import streamlit as st
import pandas as pd
import re

# 1. Настройка страницы
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

# CSS для настоящих цветных кнопок с ЧИТАЕМЫМ текстом
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Стилизация КНОПОК-ОТДЕЛОВ */
    div.stButton > button {
        height: 90px !important; border-radius: 15px !important;
        font-weight: bold !important; font-size: 16px !important;
        color: #1a1a1a !important; /* ЧЕРНЫЙ ТЕКСТ */
        border: 2px solid rgba(0,0,0,0.05) !important;
        transition: 0.3s !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }
    
    /* Индивидуальные фоновые цвета (пастельные, чтобы текст был виден) */
    div.stButton > button[key*="d_1"] { background-color: #d1d8e0 !important; } /* Админ */
    div.stButton > button[key*="d_2"] { background-color: #b8e994 !important; } /* ВЭД */
    div.stButton > button[key*="d_3"] { background-color: #fab1a0 !important; } /* Вет */
    div.stButton > button[key*="d_4"] { background-color: #ffeaa7 !important; } /* Агро */
    div.stButton > button[key*="d_5"] { background-color: #81ecec !important; } /* Корма */
    div.stButton > button[key*="d_6"] { background-color: #74b9ff !important; } /* Кадры */
    div.stButton > button[key*="d_7"] { background-color: #ffda79 !important; } /* Фин */
    div.stButton > button[key*="d_8"] { background-color: #a29bfe !important; } /* Хоз */

    /* Кнопки Назад (Светлые) */
    div.stButton > button[key*="back"] {
        background-color: #ffffff !important; height: 45px !important; color: #333 !important;
    }

    /* Карточки сотрудников */
    .card {
        background: white; border-radius: 15px; padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
        margin-bottom: 20px; border: 1px solid #e1e4e8; min-height: 380px;
    }
    .img-circle {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; margin: 0 auto 10px auto; border: 2px solid #007bff;
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
    search_q = st.text_input("🔍 Поиск...", placeholder="Кого найти?", key="search_box")

    if search_q:
        f_df = df[df['Ф.И.О.'].str.lower().str.contains(search_q.lower(), na=False) | 
                  df['Должность'].str.lower().str.contains(search_q.lower(), na=False)]
        
        if not f_df.empty:
            cols = st.columns(4)
            for i, (_, emp) in enumerate(f_df.iterrows()):
                with cols[i % 4]:
                    # Приоритет рабочего телефона
                    p_val = emp.get('Тел. Рабочий') if pd.notnull(emp.get('Тел. Рабочий')) and str(emp.get('Тел. Рабочий')).strip() != "" else emp.get('Тел. Личный')
                    phone = "".join(filter(str.isdigit, str(p_val)))
                    st.markdown(f'<div class="card"><img src="{get_photo(emp.get("Фото"))}" class="img-circle"><div style="font-weight:bold;">{emp.get("Ф.И.О.")}</div><div style="font-size:12px;color:gray;">{emp.get("Должность")}</div><br><a href="tel:+{phone}" class="btn-comm b-call">📞 Позвонить</a></div>', unsafe_allow_html=True)
        
        if st.button("✖ Сбросить поиск", key="back_from_search"):
            st.rerun()

    # СОТЫ
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

    # СПИСОК ОТДЕЛА
    else:
        if st.button("← Назад к отделам", key="back_up"):
            st.session_state.page = "home"
            st.rerun()

        f_df = df[df['d_id'] == st.session_state.page]
        cols = st.columns(4)
        for i, (_, emp) in enumerate(f_df.iterrows()):
            with cols[i % 4]:
                work_p = emp.get('Тел. Рабочий')
                priv_p = emp.get('Тел. Личный')
                final_p = work_p if pd.notnull(work_p) and str(work_p).strip() != "" else priv_p
                phone = "".join(filter(str.isdigit, str(final_p)))
                
                btns = f'<a href="tel:+{phone}" class="btn-comm b-call">📞 Позвонить</a>'
                if len(phone) > 5:
                    btns += f'<a href="https://wa.me/{phone}" class="btn-comm b-wa" target="_blank">💬 WhatsApp</a>'
                    btns += f'<a href="https://t.me/+{phone}" class="btn-comm b-tg" target="_blank">✈️ Telegram</a>'
                
                st.markdown(f'<div class="card"><img src="{get_photo(emp.get("Фото"))}" class="img-circle"><div style="font-weight:bold;min-height:40px;">{emp.get("Ф.И.О.")}</div><div style="font-size:11px;color:gray;min-height:35px;">{emp.get("Должность")}</div>{btns}</div>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("← Назад к отделам", key="back_down", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

except Exception as e:
    st.error(f"Упс! Что-то пошло не так: {e}")
