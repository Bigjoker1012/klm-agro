import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="КЛМ Справочник", layout="wide")

# Стили для кнопок и карточек
st.markdown("""
    <style>
    .employee-card {
        background-color: white; border-radius: 12px; padding: 15px;
        border: 1px solid #e0e0e0; text-align: center;
        margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .contact-btn {
        display: block; padding: 10px; color: white !important;
        text-decoration: none; border-radius: 8px; margin-top: 5px; 
        font-size: 14px; font-weight: bold;
    }
    .btn-call { background-color: #007bff; }
    .btn-wa { background-color: #28a745; }
    .btn-tg { background-color: #0088cc; }
    .btn-mail { background-color: #6c757d; }
    .stImage > img { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

def fix_drive_url(url):
    if pd.isna(url) or 'drive.google.com' not in str(url):
        return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    match = re.search(r'[-\w]{25,}', str(url))
    return f"https://drive.google.com/uc?export=view&id={match.group()}" if match else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

SHEET_URL = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df = load_data()
    
    # Сайдбар
    st.sidebar.header("🏢 Подразделения")
    depts = {
        "Все отделы": "all",
        "001 Администрация": "001",
        "002 Отдел ВЭД": "002",
        "003 Ветпрепараты": "003",
        "004 Агропродукты": "004",
        "005 Сырье и корма": "005",
        "006 Кадры / Право": "006",
        "007 Финансы": "007",
        "008 Хоз. служба": "008"
    }
    selected_dept = st.sidebar.radio("Показать:", list(depts.keys()))
    
    st.title("🧬 Справочник КЛМ")
    search = st.text_input("🔍 Поиск", "")

    # Фильтрация
    f_df = df.copy()
    if depts[selected_dept] != "all":
        # Очищаем ID от точек и нулей для поиска
        target = depts[selected_dept].lstrip('0')
        f_df['clean_id'] = f_df['ID отдела'].astype(str).str.replace(r'\.0$', '', regex=True).str.lstrip('0')
        f_df = f_df[f_df['clean_id'] == target]

    if search:
        f_df = f_df[f_df.apply(lambda x: x.astype(str).str.lower().str.contains(search.lower())).any(axis=1)]

    # Вывод карточек
    if not f_df.empty:
        cols = st.columns(3) # 3 колонки для лучшего вида кнопок
        for i, (_, emp) in enumerate(f_df.iterrows()):
            with cols[i % 3]:
                with st.container():
                    st.markdown('<div class="employee-card">', unsafe_allow_html=True)
                    
                    # Фото и Имя
                    img_url = fix_drive_url(emp.get('Фото'))
                    st.image(img_url, use_container_width=True)
                    st.markdown(f"### {emp.get('Ф.И.О.', '---')}")
                    st.write(f"*{emp.get('Должность', '-')}*")
                    
                    # Кнопки
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
