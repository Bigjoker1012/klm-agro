import streamlit as st
import pandas as pd

st.set_page_config(page_title="КЛМ Справочник", layout="wide")

# Улучшенные стили для кнопок и карточек
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .employee-card {
        background-color: white; border-radius: 15px; padding: 15px;
        border: 1px solid #eaeaea; text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        display: flex; flex-direction: column; justify-content: space-between;
        margin-bottom: 20px;
    }
    .contact-btn {
        display: block; padding: 10px; color: white !important;
        text-decoration: none; border-radius: 8px; margin-top: 6px; 
        font-size: 13px; font-weight: bold;
    }
    .btn-call { background-color: #007bff; }
    .btn-wa { background-color: #25d366; }
    .btn-tg { background-color: #0088cc; }
    .btn-mail { background-color: #6c757d; }
    .stImage > img { border-radius: 10px; object-fit: cover; }
    </style>
    """, unsafe_allow_html=True)

def fix_drive_url(url):
    if pd.isna(url) or 'drive.google.com' not in str(url):
        return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    try:
        # Универсальный перехват ID для любых ссылок Google Drive
        if '/d/' in str(url):
            file_id = str(url).split('/d/')[1].split('/')[0]
        else:
            file_id = str(url).split('id=')[1].split('&')[0]
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
    
    # Боковая панель с фильтрами
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
    search = st.text_input("🔍 Поиск по Ф.И.О. или должности", "")

    # Логика фильтрации
    f_df = df.copy()
    if depts[selected_dept] != "all":
        f_df = f_df[f_df['ID отдела'].astype(str).str.contains(depts[selected_dept], na=False)]
    
    if search:
        f_df = f_df[f_df.apply(lambda x: x.astype(str).str.lower().str.contains(search.lower())).any(axis=1)]

    # Сетка без лишних отступов сверху
    if not f_df.empty:
        cols = st.columns(4)
        for i, (_, emp) in enumerate(f_df.iterrows()):
            with cols[i % 4]:
                st.markdown('<div class="employee-card">', unsafe_allow_html=True)
                
                # Фото
                img_url = fix_drive_url(emp.get('Фото'))
                st.image(img_url, use_container_width=True)
                
                # Информация
                st.markdown(f"### {emp.get('Ф.И.О.', '---')}")
                st.write(f"*{emp.get('Должность', '-')}*")
                
                # Кнопки контактов
                # Берем мобильный, если нет — рабочий
                p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                phone = "".join(filter(str.isdigit, str(p_val)))
                
                if len(phone) > 5:
                    wa_phone = phone if phone.startswith('375') else '375' + phone[1:] if phone.startswith('80') else phone
                    st.markdown(f"""
                        <a href="tel:+{phone}" class="contact-btn btn-call">📞 Позвонить</a>
                        <a href="https://wa.me/{wa_phone}" target="_blank" class="contact-btn btn-wa">💬 WhatsApp</a>
                        <a href="https://t.me/+{phone}" target="_blank" class="contact-btn btn-tg">✈️ Telegram</a>
                    """, unsafe_allow_html=True)
                
                email = emp.get('E-mail')
                if pd.notnull(email) and "@" in str(email):
                    st.markdown(f'<a href="mailto:{email}" class="contact-btn btn-mail">✉️ Почта</a>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Никого не нашли. Попробуйте другой фильтр.")

except Exception as e:
    st.error(f"Ошибка: {e}")
