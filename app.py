import streamlit as st
import pandas as pd

st.set_page_config(page_title="КЛМ Справочник", layout="wide")

# Тюнинг интерфейса
st.markdown("""
    <style>
    .employee-card {
        background-color: white; border-radius: 12px; padding: 10px;
        border: 1px solid #eee; text-align: center; margin-bottom: 10px;
        min-height: 400px; display: flex; flex-direction: column; justify-content: space-between;
    }
    .contact-btn {
        display: block; padding: 5px; color: white !important;
        text-decoration: none; border-radius: 4px; margin-top: 3px; font-size: 11px; font-weight: bold;
    }
    .btn-call { background-color: #007bff; }
    .btn-wa { background-color: #25d366; }
    .btn-tg { background-color: #0088cc; }
    .email-text { font-size: 10px; color: #555; margin-top: 5px; word-break: break-all; }
    .stImage > img { border-radius: 50%; object-fit: cover; }
    </style>
    """, unsafe_allow_html=True)

def fix_drive_url(url):
    if pd.isna(url) or 'drive.google.com' not in str(url):
        return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    try:
        # Извлекаем ID файла корректно
        file_id = url.split('/d/')[1].split('/')[0] if '/d/' in url else url.split('id=')[1].split('&')[0]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except:
        return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

SHEET_URL = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    df = load_data()
    
    # Интерактивная легенда в сайдбаре
    st.sidebar.title("🏢 Отделы")
    depts = {
        "Все": None,
        "001 Администрация": "001",
        "002 ВЭД": "002",
        "003 Ветпрепараты": "003",
        "004 Агропродукты": "004",
        "005 Сырье и корма": "005",
        "006 Кадры / Право": "006",
        "007 Финансы": "007",
        "008 Хоз. служба": "008"
    }
    sel_dept = st.sidebar.radio("Показать отдел:", list(depts.keys()))
    
    st.title("🧬 Справочник КЛМ")
    search = st.text_input("🔍 Поиск (ФИО или Должность)", "")

    # Фильтрация данных
    filtered_df = df.copy()
    if depts[sel_dept]:
        filtered_df = filtered_df[filtered_df['ID отдела'].astype(str).str.contains(depts[sel_dept], na=False)]
    if search:
        filtered_df = filtered_df[filtered_df.apply(lambda x: x.astype(str).str.lower().str.contains(search.lower())).any(axis=1)]

    # Сетка
    cols = st.columns(5)
    for i, (_, emp) in enumerate(filtered_df.iterrows()):
        with cols[i % 5]:
            st.markdown('<div class="employee-card">', unsafe_allow_html=True)
            
            # Фото
            photo_url = fix_drive_url(emp.get('Фото'))
            st.image(photo_url, width=100)
            
            # Данные
            st.markdown(f"**{emp.get('Ф.И.О.', '---')}**")
            st.caption(f"{emp.get('Должность', '-')}")
            
            email = emp.get('E-mail')
            if pd.notnull(email):
                st.markdown(f"<div class='email-text'>✉️ {email}</div>", unsafe_allow_html=True)
            
            # Логика телефона: Личный -> Рабочий
            phone_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
            phone = "".join(filter(str.isdigit, str(phone_val)))
            
            if len(phone) > 5:
                # Корректировка для РБ
                wa_phone = phone if phone.startswith('375') else '375' + phone[1:] if phone.startswith('80') else phone
                st.markdown(f"""
                    <div style="margin-top: 10px;">
                        <a href="tel:+{phone}" class="contact-btn btn-call">📞 Позвонить</a>
                        <a href="https://wa.me/{wa_phone}" target="_blank" class="contact-btn btn-wa">💬 WhatsApp</a>
                        <a href="https://t.me/+{phone}" target="_blank" class="contact-btn btn-tg">✈️ Telegram</a>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.write("---")
            
            st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка: {e}")
