import streamlit as st
import pandas as pd
import re

# Настройка страницы
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

# CSS: Прямое окрашивание кнопок по порядку появления (надежный метод)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Общий стиль кнопок-сот */
    div.stButton > button {
        height: 100px !important; border-radius: 15px !important;
        font-weight: bold !important; font-size: 18px !important;
        color: white !important; border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }
    
    /* Цвета для 8 отделов (по порядку в сетке) */
    div.stButton:nth-of-type(1) > button { background: #4a69bd !important; } /* Админ */
    div.stButton:nth-of-type(2) > button { background: #1dd1a1 !important; } /* ВЭД */
    div.stButton:nth-of-type(3) > button { background: #ff6b6b !important; } /* Вет */
    div.stButton:nth-of-type(4) > button { background: #10ac84 !important; } /* Агро */
    div.stButton:nth-of-type(5) > button { background: #2e86de !important; } /* Корма */
    div.stButton:nth-of-type(6) > button { background: #54a0ff !important; } /* Кадры */
    div.stButton:nth-of-type(7) > button { background: #feca57 !important; } /* Фин */
    div.stButton:nth-of-type(8) > button { background: #5f27cd !important; } /* Хоз */

    /* Кнопки возврата и сброса (серые/белые) */
    .st-key-reset_btn > button, .st-key-back_up > button, .st-key-back_down > button {
        background: #f1f2f6 !important; color: #2f3542 !important; height: 50px !important;
    }

    .card {
        background: white; border-radius: 15px; padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); text-align: center;
        margin-bottom: 20px; border: 1px solid #eee; min-height: 400px;
    }
    .img-circle {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; margin: 0 auto 15px auto; border: 3px solid #f0f0f0;
    }
    .btn-comm {
        display: block; width: 100%; padding: 10px 0; margin-top: 5px;
        border-radius: 8px; font-size: 14px; font-weight: 600;
        text-decoration: none !important; color: white !important;
    }
    .b-call { background-color: #007bff; }
    .b-wa { background-color: #28a745; }
    .b-tg { background-color: #0088cc; }
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
    # Инициализация состояний
    if 'page' not in st.session_state: st.session_state.page = "home"
    if 'search_val' not in st.session_state: st.session_state.search_val = ""

    st.markdown("<h2 style='text-align: center;'>Справочник КЛМ</h2>", unsafe_allow_html=True)

    # 1. ПОИСК (С механизмом очистки)
    search_query = st.text_input("🔍 Поиск сотрудника", value=st.session_state.search_val, placeholder="Фамилия...", key="main_search_input")

    if search_query:
        f_df = df[df['Ф.И.О.'].str.lower().str.contains(search_query.lower(), na=False) | 
                  df['Должность'].str.lower().str.contains(search_query.lower(), na=False)]
        
        if not f_df.empty:
            st.info(f"Найдено: {len(f_df)}")
            cols = st.columns(4)
            for i, (_, emp) in enumerate(f_df.iterrows()):
                with cols[i % 4]:
                    # Приоритет рабочего телефона
                    w_phone = str(emp.get('Тел. Рабочий', '')).strip()
                    l_phone = str(emp.get('Тел. Личный', '')).strip()
                    final_phone = w_phone if w_phone != "nan" and w_phone != "" else l_phone
                    clean_phone = "".join(filter(str.isdigit, final_phone))
                    
                    st.markdown(f'<div class="card"><img src="{get_photo(emp.get("Фото"))}" class="img-circle"><div style="font-weight:bold;height:45px;">{emp.get("Ф.И.О.")}</div><div style="font-size:12px;color:gray;height:40px;">{emp.get("Должность")}</div><br><a href="tel:+{clean_phone}" class="btn-comm b-call">📞 Позвонить</a></div>', unsafe_allow_html=True)
        
        if st.button("✖ Сбросить поиск и вернуться", key="reset_btn"):
            st.session_state.search_val = ""
            st.rerun()

    # 2. ГЛАВНЫЙ ЭКРАН (СОТЫ)
    elif st.session_state.page == "home":
        depts = [
            ("Администрация", 1), ("Отдел ВЭД", 2), ("Ветпрепараты", 3), ("Агропродукты", 4),
            ("Сырье и корма", 5), ("Кадры / Право", 6), ("Финансы", 7), ("Хоз. служба", 8)
        ]
        # Рисуем сетку 2x4
        for r in range(0, 8, 4):
            cols = st.columns(4)
            for i, (name, d_id) in enumerate(depts[r:r+4]):
                with cols[i]:
                    if st.button(name, key=f"d_{d_id}", use_container_width=True):
                        st.session_state.page = d_id
                        st.rerun()

    # 3. СПИСОК ОТДЕЛА
    else:
        if st.button("← Назад к отделам", key="back_up"):
            st.session_state.page = "home"
            st.rerun()

        f_df = df[df['d_id'] == st.session_state.page]
        cols = st.columns(4)
        for i, (_, emp) in enumerate(f_df.iterrows()):
            with cols[i % 4]:
                w_phone = str(emp.get('Тел. Рабочий', '')).strip()
                l_phone = str(emp.get('Тел. Личный', '')).strip()
                final_p = w_phone if w_phone != "nan" and w_phone != "" else l_phone
                phone = "".join(filter(str.isdigit, final_p))
                
                btns = f'<a href="tel:+{phone}" class="btn-comm b-call">📞 Позвонить</a>'
                if len(phone) > 5:
                    btns += f'<a href="https://wa.me/{phone}" class="btn-comm b-wa" target="_blank">💬 WhatsApp</a>'
                    btns += f'<a href="https://t.me/+{phone}" class="btn-comm b-tg" target="_blank">✈️ Telegram</a>'
                
                st.markdown(f'<div class="card"><img src="{get_photo(emp.get("Фото"))}" class="img-circle"><div style="font-weight:bold;height:40px;">{emp.get("Ф.И.О.")}</div><div style="font-size:11px;color:gray;height:35px;">{emp.get("Должность")}</div>{btns}</div>', unsafe_allow_html=True)

        st.write("---")
        if st.button("← Назад к списку отделов", key="back_down", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

except Exception as e:
    st.error(f"Системное уведомление: {e}")
