import streamlit as st
import pandas as pd
import re

# 1. Настройка страницы
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

# CSS для настоящих цветных "Сот" и фиксации интерфейса
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Стилизация ввода поиска */
    .stTextInput > div > div > input {
        border-radius: 25px; border: 2px solid #007bff; padding: 12px 20px;
    }

    /* Карточки сотрудников */
    .card {
        background: white; border-radius: 15px; padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
        margin-bottom: 20px; border: 1px solid #e1e4e8; min-height: 420px;
        display: flex; flex-direction: column;
    }
    .img-circle {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; margin: 0 auto 10px auto; border: 3px solid #007bff;
    }
    
    /* Кнопки мессенджеров */
    .btn-comm {
        display: block; width: 100%; padding: 10px 0; margin-top: 5px;
        border-radius: 8px; font-size: 13px; font-weight: 600;
        text-decoration: none !important; color: white !important; text-align: center;
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
    
    # Инициализация состояний
    if 'page' not in st.session_state: st.session_state.page = "home"
    if 'search_val' not in st.session_state: st.session_state.search_val = ""

    st.markdown("<h1 style='text-align: center;'>Справочник КЛМ</h1>", unsafe_allow_html=True)

    # ПОИСК НА ГЛАВНОЙ
    search_query = st.text_input("Поиск сотрудника", value=st.session_state.search_val, 
                                 placeholder="Введите фамилию или должность...", label_visibility="collapsed")

    # ЛОГИКА: Если что-то введено в поиск - показываем результат
    if search_query:
        f_df = df[df['Ф.И.О.'].str.lower().str.contains(search_query.lower()) | 
                  df['Должность'].str.lower().str.contains(search_query.lower())]
        
        if not f_df.empty:
            st.success(f"Найдено: {len(f_df)}")
            cols = st.columns(4)
            for i, (_, emp) in enumerate(f_df.iterrows()):
                with cols[i % 4]:
                    p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                    phone = "".join(filter(str.isdigit, str(p_val)))
                    st.markdown(f"""
                        <div class="card">
                            <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                            <div style="font-weight:bold; height:45px;">{emp.get('Ф.И.О.')}</div>
                            <div style="font-size:12px; color:gray; height:40px;">{emp.get('Должность')}</div>
                            <a href="tel:+{phone}" class="btn-comm b-call">📞 Позвонить</a>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Ничего не найдено")
        
        if st.button("✖ Сбросить поиск и вернуться к сотам"):
            st.session_state.search_val = ""
            st.rerun()

    # ГЛАВНЫЙ ЭКРАН (ЦВЕТНОЙ УЛЕЙ)
    elif st.session_state.page == "home":
        st.write("### Структура компании:")
        
        # Список отделов с привязкой к ID
        depts = [
            ("🏢 Администрация", 1), ("🌍 Отдел ВЭД", 2), ("💊 Ветпрепараты", 3), ("🚜 Агропродукты", 4),
            ("🌾 Сырье и корма", 5), ("⚖️ Кадры / Право", 6), ("💰 Финансы", 7), ("🛠️ Хоз. служба", 8)
        ]
        
        # Создаем сетку 2x4 (как соты)
        for row in range(0, len(depts), 4):
            cols = st.columns(4)
            for i, (name, d_id) in enumerate(depts[row:row+4]):
                with cols[i]:
                    # Используем type="primary" для раскраски
                    if st.button(name, key=f"btn_{d_id}", use_container_width=True, type="primary"):
                        st.session_state.page = d_id
                        st.rerun()

    # СТРАНИЦА КОНКРЕТНОГО ОТДЕЛА
    else:
        if st.button("← Назад к разделам"):
            st.session_state.page = "home"
            st.rerun()

        f_df = df[df['d_id'] == st.session_state.page]
        cols = st.columns(4)
        for i, (_, emp) in enumerate(f_df.iterrows()):
            with cols[i % 4]:
                p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                phone = "".join(filter(str.isdigit, str(p_val)))
                
                # Кнопки связи
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
    st.error(f"Произошла ошибка: {e}")
