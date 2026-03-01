import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="КЛМ Справочник", layout="wide")

# CSS стили
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .employee-card {
        background-color: white; border-radius: 15px; padding: 20px;
        border: 1px solid #e0e0e0; text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .contact-btn {
        display: block; padding: 10px; color: white !important;
        text-decoration: none; border-radius: 8px; margin-top: 8px; 
        font-size: 14px; font-weight: bold; text-align: center;
    }
    .btn-call { background-color: #007bff; }
    .btn-wa { background-color: #28a745; }
    .btn-tg { background-color: #0088cc; }
    .btn-mail { background-color: #6c757d; }
    
    .stImage img {
        width: 110px !important;
        height: 110px !important;
        object-fit: cover;
        margin: 0 auto;
        border-radius: 50%;
        border: 3px solid #f0f2f5;
    }
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

def fix_drive_url(url):
    if pd.isna(url):
        return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    
    url_str = str(url).strip()
    
    # Если это уже прямая ссылка, оставляем как есть
    if 'drive.google.com/uc?' in url_str:
        return url_str
        
    # Ищем ID файла (длинный код из букв и цифр)
    match = re.search(r'[-\w]{25,}', url_str)
    if match:
        file_id = match.group()
        # Генерируем прямую ссылку для отображения картинки
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    
    return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

SHEET_URL = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"

# Убрали кэш на время отладки фото (ttl=0), чтобы данные всегда были свежие
@st.cache_data(ttl=0) 
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = [str(c).strip() for c in df.columns]
    if 'ID отдела' in df.columns:
        df['dept_num'] = pd.to_numeric(df['ID отдела'], errors='coerce').fillna(0).astype(int)
    return df

try:
    df = load_data()
    
    # Фильтры в сайдбаре
    st.sidebar.header("🏢 Подразделения")
    depts_map = {
        "Все отделы": "all",
        "001 Администрация": 1,
        "002 Отдел ВЭД": 2,
        "003 Ветпрепараты": 3,
        "004 Агропродукты": 4,
        "005 Сырье и корма": 5,
        "006 Кадры / Право": 6,
        "007 Финансы": 7,
        "008 Хоз. служба": 8
    }
    selected_dept = st.sidebar.radio("Показать:", list(depts_map.keys()))
    
    st.title("🧬 Справочник КЛМ")
    search = st.text_input("🔍 Поиск", placeholder="Введите фамилию...")

    f_df = df.copy()
    if depts_map[selected_dept] != "all":
        f_df = f_df[f_df['dept_num'] == depts_map[selected_dept]]
    
    if search:
        f_df = f_df[f_df.apply(lambda x: x.astype(str).str.lower().str.contains(search.lower())).any(axis=1)]

    if not f_df.empty:
        f_df = f_df.sort_values('Ф.И.О.')
        cols = st.columns(4)
        for i, (_, emp) in enumerate(f_df.iterrows()):
            with cols[i % 4]:
                st.markdown('<div class="employee-card">', unsafe_allow_html=True)
                
                # Фото
                raw_photo_link = emp.get('Фото')
                img_url = fix_drive_url(raw_photo_link)
                
                # Выводим картинку
                st.image(img_url, width=110)
                
                # Имя и должность
                st.markdown(f"**{emp.get('Ф.И.О.', '---')}**")
                st.markdown(f"<div style='font-size: 11px; color: gray; height: 30px;'>{emp.get('Должность', '-')}</div>", unsafe_allow_html=True)
                
                # Контакты
                p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                phone = "".join(filter(str.isdigit, str(p_val)))
                
                if len(phone) > 5:
                    clean_phone = f"+{phone}" if not str(phone).startswith('+') else phone
                    wa_phone = phone if phone.startswith('375') else '375' + phone[1:] if phone.startswith('80') else phone
                    
                    st.markdown(f'<a href="tel:{clean_phone}" class="contact-btn btn-call">📞 Позвонить</a>', unsafe_allow_html=True)
                    st.markdown(f'<a href="https://wa.me/{wa_phone}" target="_blank" class="contact-btn btn-wa">💬 WhatsApp</a>', unsafe_allow_html=True)
                    st.markdown(f'<a href="https://t.me/+{phone}" target="_blank" class="contact-btn btn-tg">✈️ Telegram</a>', unsafe_allow_html=True)
                
                email = emp.get('E-mail')
                if pd.notnull(email) and "@" in str(email):
                    st.markdown(f'<a href="mailto:{email}" class="contact-btn btn-mail">✉️ Почта</a>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Сотрудники не найдены.")

except Exception as e:
    st.error(f"Ошибка загрузки данных: {e}")
