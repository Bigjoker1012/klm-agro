import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="КЛМ Справочник", layout="wide")

# Тюнинг интерфейса: плотная верстка и маленькие фото
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    /* Карточка сотрудника без лишних отступов */
    .employee-card {
        background-color: white; border-radius: 12px; padding: 15px;
        border: 1px solid #e0e0e0; text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-top: 0px !important;
    }
    /* Кнопки-контакты */
    .contact-btn {
        display: block; padding: 8px; color: white !important;
        text-decoration: none; border-radius: 6px; margin-top: 5px; 
        font-size: 13px; font-weight: bold; text-align: center;
    }
    .btn-call { background-color: #007bff; }
    .btn-wa { background-color: #28a745; }
    .btn-tg { background-color: #0088cc; }
    .btn-mail { background-color: #6c757d; }
    
    /* Уменьшаем фото в 2 раза */
    .stImage img {
        max-width: 120px !important;
        margin-left: auto;
        margin-right: auto;
        border-radius: 50%;
    }
    </style>
    """, unsafe_allow_html=True)

def fix_drive_url(url):
    if pd.isna(url) or 'drive.google.com' not in str(url):
        return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    match = re.search(r'[-\w]{25,}', str(url))
    return f"https://drive.google.com/uc?export=view&id={match.group()}" if match else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

SHEET_URL = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"

@st.cache_data(ttl=2)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = [str(c).strip() for c in df.columns]
    if 'ID отдела' in df.columns:
        # Приводим к формату '5', '7' и т.д. без нулей и точек
        df['dept_id'] = df['ID отдела'].astype(str).str.replace(r'\.0$', '', regex=True).str.lstrip('0').str.strip()
    return df

try:
    df = load_data()
    
    # Легенда в сайдбаре
    st.sidebar.header("🏢 Подразделения")
    depts = {
        "Все отделы": "all",
        "001 Администрация": "1",
        "002 Отдел ВЭД": "2",
        "003 Ветпрепараты": "3",
        "004 Агропродукты": "4",
        "005 Сырье и корма": "5",
        "006 Кадры / Право": "6",
        "007 Финансы": "7",
        "008 Хоз. служба": "8"
    }
    selected_dept = st.sidebar.radio("Показать:", list(depts.keys()))
    
    st.title("🧬 Справочник КЛМ")
    search = st.text_input("🔍 Поиск по ФИО или должности", "")

    # Фильтрация
    f_df = df.copy()
    if depts[selected_dept] != "all":
        f_df = f_df[f_df['dept_id'] == depts[selected_dept]]
    
    if search:
        f_df = f_df[f_df.apply(lambda x: x.astype(str).str.lower().str.contains(search.lower())).any(axis=1)]

    # Сетка без пустых верхних рядов
    if not f_df.empty:
        f_df = f_df.sort_values('Ф.И.О.')
        cols = st.columns(4)
        for i, (_, emp) in enumerate(f_df.iterrows()):
            with cols[i % 4]:
                # Все данные теперь в одном контейнере без разрывов
                st.markdown('<div class="employee-card">', unsafe_allow_html=True)
                
                # Компактное фото
                img_url = fix_drive_url(emp.get('Фото'))
                st.image(img_url, use_container_width=False, width=120)
                
                st.markdown(f"**{emp.get('Ф.И.О.', '---')}**")
                st.markdown(f"<div style='font-size: 12px; color: gray; height: 35px;'>{emp.get('Должность', '-')}</div>", unsafe_allow_html=True)
                
                # Кнопки контактов
                p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                phone = "".join(filter(str.isdigit, str(p_val)))
                
                if len(phone) > 5:
                    wa_phone = phone if phone.startswith('375') else '375' + phone[1:] if phone.startswith('80') else phone
                    st.markdown(f'<a href="tel:+{phone}" class="contact-btn btn-call">📞 Позвонить</a>', unsafe_allow_html=True)
                    st.markdown(f'<a href="https://wa.me/{wa_phone}" target="_blank" class="contact-btn btn-wa">💬 WhatsApp</a>', unsafe_allow_html=True)
                    st.markdown(f'<a href="https://t.me/+{phone}" target="_blank" class="contact-btn btn-tg">✈️ Telegram</a>', unsafe_allow_html=True)
                
                email = emp.get('E-mail')
                if pd.notnull(email) and "@" in str(email):
                    st.markdown(f'<a href="mailto:{email}" class="contact-btn btn-mail">✉️ Почта</a>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Никого не нашли.")

except Exception as e:
    st.error(f"Ошибка: {e}")
