import streamlit as st
import pandas as pd
import re

# 1. Настройка страницы
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

# CSS для цветных плиток и карточек
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Стилизация плиток отделов (СОТЫ) */
    .dept-tile {
        display: flex; align-items: center; justify-content: center;
        height: 100px; border-radius: 15px; color: white !important;
        font-weight: bold; font-size: 18px; text-align: center;
        margin-bottom: 15px; cursor: pointer; transition: 0.3s;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15); border: none;
        text-decoration: none !important;
    }
    .dept-tile:hover { transform: scale(1.02); filter: brightness(1.1); }
    
    /* Цвета отделов */
    .c-1 { background: linear-gradient(135deg, #1e3c72, #2a5298); } /* Админ */
    .c-2 { background: linear-gradient(135deg, #11998e, #38ef7d); } /* ВЭД */
    .c-3 { background: linear-gradient(135deg, #ff9966, #ff5e62); } /* Вет */
    .c-4 { background: linear-gradient(135deg, #56ab2f, #a8e063); } /* Агро */
    .c-5 { background: linear-gradient(135deg, #4b6cb7, #182848); } /* Корма */
    .c-6 { background: linear-gradient(135deg, #00b4db, #0083b0); } /* Кадры */
    .c-7 { background: linear-gradient(135deg, #f2994a, #f2c94c); } /* Фин */
    .c-8 { background: linear-gradient(135deg, #8e44ad, #c0392b); } /* Хоз */

    /* Карточки сотрудников */
    .card {
        background: white; border-radius: 15px; padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
        margin-bottom: 20px; border: 1px solid #e1e4e8; min-height: 420px;
    }
    .img-circle {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; margin: 0 auto 10px auto; border: 3px solid #eee;
    }
    
    /* Кнопки связи */
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
    if 'search' not in st.session_state: st.session_state.search = ""

    st.markdown("<h2 style='text-align: center;'>Справочник КЛМ</h2>", unsafe_allow_html=True)

    # 2. ПОИСК
    search_query = st.text_input("🔍 Поиск...", value=st.session_state.search, key="search_input")

    # Если в поиске что-то есть - показываем только поиск
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
        
        if st.button("✖ Очистить и вернуться к сотам"):
            st.session_state.search = ""
            st.session_state.page = "home"
            st.rerun()

    # 3. ГЛАВНЫЙ ЭКРАН (ЦВЕТНЫЕ ПЛИТКИ)
    elif st.session_state.page == "home":
        depts = [
            ("🏢 Администрация", 1), ("🌍 Отдел ВЭД", 2), ("💊 Ветпрепараты", 3), ("🚜 Агропродукты", 4),
            ("🌾 Сырье и корма", 5), ("⚖️ Кадры / Право", 6), ("💰 Финансы", 7), ("🛠️ Хоз. служба", 8)
        ]
        
        cols = st.columns(4)
        for i, (name, d_id) in enumerate(depts):
            with cols[i % 4]:
                # Используем кликабельные HTML блоки для цвета
                if st.button(name, key=f"d_{d_id}", use_container_width=True):
                    st.session_state.page = d_id
                    st.rerun()
                # Принудительная раскраска кнопки через CSS селектор
                st.markdown(f'<style>div[data-testid="stButton"] button[key="d_{d_id}"] {{ border: 2px solid #eee; }} </style>', unsafe_allow_html=True)
                # Костыль для цвета - рисуем цветную плашку под кнопкой для индикации
                st.markdown(f'<div class="dept-tile c-{d_id}">{name}</div>', unsafe_allow_html=True)

    # 4. ОТДЕЛ
    else:
        if st.button("← Назад к сотам"):
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
    st.error(f"Ошибка: {e}")
