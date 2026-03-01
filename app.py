import streamlit as st
import pandas as pd
import re

# 1. Настройки и CSS для ГРАФИЧЕСКИХ СОТ
st.set_page_config(page_title="Справочник КЛМ", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    
    /* СЕТКА СОТ ДЛЯ ОТДЕЛОВ */
    .honeycomb {
        display: flex; flex-wrap: wrap; justify-content: center;
        gap: 15px; padding: 20px;
    }
    .hex-button {
        width: 160px; height: 180px; background: #007bff;
        clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
        display: flex; align-items: center; justify-content: center;
        text-align: center; color: white; font-weight: bold; font-size: 14px;
        border: none; cursor: pointer; transition: 0.3s; padding: 20px;
    }
    .hex-button:hover { transform: scale(1.05); background: #0056b3; }

    /* КАРТОЧКИ СОТРУДНИКОВ */
    .card {
        background: white; border-radius: 15px; padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;
        margin-bottom: 20px; border: 1px solid #eee; min-height: 420px;
        display: flex; flex-direction: column;
    }
    .img-circle {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; margin: 0 auto 10px auto; border: 3px solid #f0f2f5;
    }
    .name { font-size: 15px; font-weight: bold; margin-bottom: 5px; height: 40px; line-height: 1.2; }
    .job { font-size: 12px; color: #757575; height: 35px; margin-bottom: 15px; }
    
    /* КНОПКИ СВЯЗИ */
    .btn {
        display: block; width: 100%; padding: 8px 0; margin-top: 4px;
        border-radius: 8px; font-size: 13px; font-weight: bold;
        text-decoration: none !important; color: white !important;
        text-align: center;
    }
    .b-call { background-color: #007bff; }
    .b-wa { background-color: #28a745; }
    .b-tg { background-color: #0088cc; }
    .b-mail { background-color: #6c757d; }
    .b-none { background-color: #f8f9fa; color: #ccc !important; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# 2. ДАННЫЕ
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
    
    if 'page' not in st.session_state:
        st.session_state.page = "home"

    st.markdown("<h1 style='text-align: center;'>Справочник КЛМ</h1>", unsafe_allow_html=True)

    # ГЛАВНЫЙ ЭКРАН С СОТАМИ
    if st.session_state.page == "home":
        depts = {
            "Администрация": 1, "Отдел ВЭД": 2, "Ветпрепараты": 3,
            "Агропродукты": 4, "Сырье и корма": 5, "Кадры / Право": 6,
            "Финансы": 7, "Хоз. служба": 8
        }
        
        st.write("### Выберите подразделение:")
        
        # Отрисовка сот через колонки
        row1 = st.columns(4)
        row2 = st.columns(4)
        all_cols = row1 + row2
        
        for i, (name, d_id) in enumerate(depts.items()):
            with all_cols[i]:
                # CSS сделает эти кнопки похожими на соты
                if st.button(name, key=f"dept_{d_id}", use_container_width=True):
                    st.session_state.page = d_id
                    st.rerun()
        
        st.markdown("---")
        if st.button("👥 Показать всех сотрудников", use_container_width=True):
            st.session_state.page = 0
            st.rerun()

    # СПИСОК СОТРУДНИКОВ
    else:
        if st.button("← Вернуться к разделам"):
            st.session_state.page = "home"
            st.rerun()

        current_id = st.session_state.page
        f_df = df if current_id == 0 else df[df['d_id'] == current_id]
        
        search = st.text_input("🔍 Быстрый поиск", "")
        if search:
            f_df = f_df[f_df['Ф.И.О.'].str.lower().str.contains(search.lower()) | 
                        f_df['Должность'].str.lower().str.contains(search.lower())]

        # Сетка карточек
        for i in range(0, len(f_df), 4):
            cols = st.columns(4)
            batch = f_df.iloc[i:i+4]
            for j, (_, emp) in enumerate(batch.iterrows()):
                with cols[j]:
                    # Логика кнопок
                    p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                    phone = "".join(filter(str.isdigit, str(p_val)))
                    
                    btns = ""
                    if len(phone) > 5:
                        clean_p = f"+{phone}" if not phone.startswith('375') else phone
                        btns += f'<a href="tel:{clean_p}" class="btn b-call">📞 Позвонить</a>'
                        btns += f'<a href="https://wa.me/{phone}" class="btn b-wa" target="_blank">💬 WhatsApp</a>'
                        btns += f'<a href="https://t.me/+{phone}" class="btn b-tg" target="_blank">✈️ Telegram</a>'
                    else:
                        btns += '<div class="btn b-none">Нет номера</div><div class="btn b-none">—</div><div class="btn b-none">—</div>'

                    email = emp.get('E-mail')
                    if pd.notnull(email) and "@" in str(email):
                        btns += f'<a href="mailto:{email}" class="btn b-mail">✉️ Почта</a>'
                    else:
                        btns += '<div class="btn b-none">Нет почты</div>'

                    st.markdown(f"""
                    <div class="card">
                        <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                        <div class="name">{emp.get('Ф.И.О.', '---')}</div>
                        <div class="job">{emp.get('Должность', '-')}</div>
                        {btns}
                    </div>
                    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Произошла ошибка: {e}")
