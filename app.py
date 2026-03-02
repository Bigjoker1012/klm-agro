import streamlit as st
import pandas as pd
import re

# 1. Настройка страницы
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

# ЖЕЛЕЗНЫЙ CSS для цветных плиток и читаемости
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Контейнер для плиток */
    .main-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        padding: 10px;
    }
    
    /* Стилизация ПЛИТОК (вместо стандартных кнопок) */
    .dept-tile {
        height: 120px;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white !important;
        font-weight: bold;
        font-size: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: 0.3s;
        text-decoration: none !important;
    }
    .dept-tile:hover { transform: translateY(-5px); box-shadow: 0 6px 20px rgba(0,0,0,0.2); }

    /* Цвета отделов */
    .bg-admin { background: linear-gradient(135deg, #2c3e50, #4ca1af); }
    .bg-ved { background: linear-gradient(135deg, #11998e, #38ef7d); }
    .bg-vet { background: linear-gradient(135deg, #ff9966, #ff5e62); }
    .bg-agro { background: linear-gradient(135deg, #56ab2f, #a8e063); }
    .bg-feed { background: linear-gradient(135deg, #4b6cb7, #182848); }
    .bg-hr { background: linear-gradient(135deg, #00b4db, #0083b0); }
    .bg-fin { background: linear-gradient(135deg, #f2994a, #f2c94c); }
    .bg-hoz { background: linear-gradient(135deg, #8e44ad, #c0392b); }

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

    # ПОИСК
    search_q = st.text_input("🔍 Быстрый поиск", placeholder="Введите фамилию или должность...", key="search")

    if search_q:
        results = df[df['Ф.И.О.'].str.lower().str.contains(search_q.lower(), na=False) | 
                     df['Должность'].str.lower().str.contains(search_q.lower(), na=False)]
        
        if not results.empty:
            st.success(f"Найдено сотрудников: {len(results)}")
            cols = st.columns(4)
            for i, (_, emp) in enumerate(results.iterrows()):
                with cols[i % 4]:
                    w_p = str(emp.get('Тел. Рабочий', '')).strip()
                    l_p = str(emp.get('Тел. Личный', '')).strip()
                    phone = w_p if w_p not in ["nan", ""] else l_p
                    clean_phone = "".join(filter(str.isdigit, phone))
                    
                    st.markdown(f"""
                        <div class="emp-card">
                            <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                            <div style="font-weight:bold; font-size:16px;">{emp.get('Ф.И.О.')}</div>
                            <div style="color:gray; font-size:13px; margin-bottom:15px;">{emp.get('Должность')}</div>
                            <a href="tel:+{clean_phone}" class="call-btn">📞 Позвонить</a>
                        </div>
                    """, unsafe_allow_html=True)
        
        if st.button("✖ Сбросить поиск", use_container_width=True):
            st.rerun()

    # ГЛАВНЫЙ ЭКРАН (Цветные плитки)
    elif st.session_state.page == "home":
        depts = [
            ("🏢 Администрация", 1, "bg-admin"), ("🌍 Отдел ВЭД", 2, "bg-ved"), 
            ("💊 Ветпрепараты", 3, "bg-vet"), ("🚜 Агропродукты", 4, "bg-agro"),
            ("🌾 Сырье и корма", 5, "bg-feed"), ("⚖️ Кадры / Право", 6, "bg-hr"), 
            ("💰 Финансы", 7, "bg-fin"), ("🛠️ Хоз. служба", 8, "bg-hoz")
        ]
        
        cols = st.columns(4)
        for i, (name, d_id, color_class) in enumerate(depts):
            with cols[i % 4]:
                if st.button(name, key=f"btn_{d_id}", use_container_width=True):
                    st.session_state.page = d_id
                    st.rerun()
                # Дублируем цветом через Markdown, чтобы точно прокрасилось
                st.markdown(f'<div class="dept-tile {color_class}">{name}</div>', unsafe_allow_html=True)

    # СПИСОК ОТДЕЛА
    else:
        if st.button("← Назад к сотам", key="back_up", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

        dept_df = df[df['d_id'] == st.session_state.page]
        cols = st.columns(4)
        for i, (_, emp) in enumerate(dept_df.iterrows()):
            with cols[i % 4]:
                w_p = str(emp.get('Тел. Рабочий', '')).strip()
                l_p = str(emp.get('Тел. Личный', '')).strip()
                phone = w_p if w_p not in ["nan", ""] else l_p
                clean_phone = "".join(filter(str.isdigit, phone))
                
                st.markdown(f"""
                    <div class="emp-card">
                        <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                        <div style="font-weight:bold;">{emp.get('Ф.И.О.')}</div>
                        <div style="color:gray; font-size:12px; margin-bottom:10px;">{emp.get('Должность')}</div>
                        <a href="tel:+{clean_phone}" class="call-btn">📞 Позвонить</a>
                    </div>
                """, unsafe_allow_html=True)

        st.write("---")
        if st.button("← Вернуться к выбору отдела", key="back_down", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

except Exception as e:
    st.error(f"Ошибка загрузки: {e}")
