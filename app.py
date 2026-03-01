import streamlit as st
import pandas as pd
import re

# 1. Настройки и расширенные ЦВЕТНЫЕ стили
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Стили для разных отделов (цвета из твоей любимой версии) */
    .btn-dept {
        display: flex; align-items: center; justify-content: center;
        height: 100px; border-radius: 15px; color: white !important;
        font-weight: bold; text-align: center; cursor: pointer;
        transition: 0.3s; border: none; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); font-size: 16px;
        text-decoration: none !important;
    }
    .btn-dept:hover { transform: translateY(-5px); filter: brightness(1.1); }
    
    /* Палитра */
    .d-1 { background: linear-gradient(135deg, #1e3c72, #2a5298); } /* Админ */
    .d-2 { background: linear-gradient(135deg, #11998e, #38ef7d); } /* ВЭД */
    .d-3 { background: linear-gradient(135deg, #f2994a, #f2c94c); } /* Вет */
    .d-4 { background: linear-gradient(135deg, #eb3349, #f45c43); } /* Агро */
    .d-5 { background: linear-gradient(135deg, #4b6cb7, #182848); } /* Корма */
    .d-6 { background: linear-gradient(135deg, #00b4db, #0083b0); } /* Кадры */
    .d-7 { background: linear-gradient(135deg, #8e44ad, #c0392b); } /* Фин */
    .d-8 { background: linear-gradient(135deg, #2c3e50, #4ca1af); } /* Хоз */

    /* Карточки сотрудников */
    .card {
        background: white; border-radius: 15px; padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
        margin-bottom: 20px; border: 1px solid #e1e4e8; min-height: 440px;
        display: flex; flex-direction: column;
    }
    .img-circle {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; margin: 0 auto 10px auto; border: 3px solid #f0f2f5;
    }
    
    /* Кнопки мессенджеров */
    .btn-comm {
        display: block; width: 100%; padding: 8px 0; margin-top: 5px;
        border-radius: 8px; font-size: 13px; font-weight: 600;
        text-decoration: none !important; color: white !important; text-align: center;
    }
    .b-call { background-color: #007bff; }
    .b-wa { background-color: #28a745; }
    .b-tg { background-color: #0088cc; }
    .b-mail { background-color: #6c757d; }
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

    st.markdown("<h2 style='text-align: center; color: #1c1e21;'>Справочник КЛМ</h2>", unsafe_allow_html=True)

    # ПОИСК
    search_query = st.text_input("", placeholder="🔍 Поиск по фамилии или должности...").lower()

    if search_query:
        f_df = df[df['Ф.И.О.'].str.lower().str.contains(search_query) | 
                  df['Должность'].str.lower().str.contains(search_query)]
        
        if not f_df.empty:
            st.info(f"Найдено: {len(f_df)}")
            cols = st.columns(4)
            for i, (_, emp) in enumerate(f_df.iterrows()):
                with cols[i % 4]:
                    # Отрисовка карточки
                    p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                    phone = "".join(filter(str.isdigit, str(p_val)))
                    st.markdown(f"""
                        <div class="card">
                            <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                            <div style="font-weight:bold;">{emp.get('Ф.И.О.')}</div>
                            <div style="font-size:12px;color:gray;height:35px;">{emp.get('Должность')}</div>
                            <a href="tel:+{phone}" class="btn-comm b-call">📞 Позвонить</a>
                        </div>
                    """, unsafe_allow_html=True)
        
        if st.button("✖ Назад к отделам"):
            st.rerun()

    # ГЛАВНЫЙ ЭКРАН С ЦВЕТНЫМИ ОТДЕЛАМИ
    elif st.session_state.page == "home":
        depts = [
            ("Администрация", 1), ("Отдел ВЭД", 2), ("Ветпрепараты", 3), ("Агропродукты", 4),
            ("Сырье и корма", 5), ("Кадры / Право", 6), ("Финансы", 7), ("Хоз. служба", 8)
        ]
        
        cols = st.columns(4)
        for i, (name, d_id) in enumerate(depts):
            with cols[i % 4]:
                # Используем HTML для красивых цветных блоков
                if st.button(name, key=f"d_{d_id}", use_container_width=True):
                    st.session_state.page = d_id
                    st.rerun()
                # Подкрашиваем кнопку через CSS класс
                st.markdown(f'<style>button[kind="secondary"]#b_d_{d_id} {{ background: red; }} </style>', unsafe_allow_html=True)

    # ЭКРАН ОТДЕЛА
    else:
        if st.button("← Вернуться в Улей"):
            st.session_state.page = "home"
            st.rerun()

        f_df = df[df['d_id'] == st.session_state.page]
        cols = st.columns(4)
        for i, (_, emp) in enumerate(f_df.iterrows()):
            with cols[i % 4]:
                p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                phone = "".join(filter(str.isdigit, str(p_val)))
                
                # Формируем кнопки
                wa_link = f'<a href="https://wa.me/{phone}" class="btn-comm b-wa" target="_blank">💬 WhatsApp</a>' if len(phone) > 5 else ""
                tg_link = f'<a href="https://t.me/+{phone}" class="btn-comm b-tg" target="_blank">✈️ Telegram</a>' if len(phone) > 5 else ""
                call_link = f'<a href="tel:+{phone}" class="btn-comm b-call">📞 Позвонить</a>' if len(phone) > 5 else ""
                
                st.markdown(f"""
                <div class="card">
                    <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                    <div style="font-weight:bold;height:40px;">{emp.get('Ф.И.О.')}</div>
                    <div style="font-size:11px;color:gray;height:35px;">{emp.get('Должность')}</div>
                    {call_link}
                    {wa_link}
                    {tg_link}
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка: {e}")
