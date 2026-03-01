import streamlit as st
import pandas as pd

st.set_page_config(page_title="КЛМ Справочник", layout="wide")

# Чистый стиль без "глючных" сот
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stColumn > div {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        text-align: center;
    }
    .contact-link {
        display: block;
        background: #007bff;
        color: white !important;
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
    }
    .contact-link:hover { background: #0056b3; }
    .wa { background: #25d366; }
    .tg { background: #0088cc; }
    </style>
    """, unsafe_allow_html=True)

def fix_drive_url(url):
    if pd.isna(url) or 'drive.google.com' not in str(url):
        return "https://via.placeholder.com/150?text=No+Photo"
    try:
        file_id = url.split('/')[-2] if '/view' in url else url.split('=')[-1]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except: return "https://via.placeholder.com/150"

SHEET_URL = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"

@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    st.title("🧬 Справочник КЛМ")
    
    search = st.text_input("🔍 Поиск", "").lower()
    display_df = df[df.apply(lambda x: x.astype(str).str.lower().str.contains(search)).any(axis=1)] if search else df

    cols = st.columns(3) # 3 в ряд для наглядности

    for i, (_, row) in enumerate(display_df.iterrows()):
        with cols[i % 3]:
            # Фото
            img_url = fix_drive_url(row.get('Фото', ''))
            st.image(img_url, width=200)
            
            # Инфо
            st.markdown(f"### {row.get('Ф.И.О.', '')}")
            st.write(f"**{row.get('Должность', '')}**")
            
            dept_id = str(row.get('ID отдела', '')).replace('.0', '').zfill(3)
            st.caption(f"Отдел: {dept_id}")
            
            # Кнопки связи
            phone = str(row.get('Тел. Личный', '')).replace(" ", "").replace("-", "")
            if phone and phone != 'nan':
                wa_phone = phone.replace('+', '')
                st.markdown(f"""
                    <a href="tel:{phone}" class="contact-link">📞 Позвонить</a>
                    <a href="https://wa.me/{wa_phone}" target="_blank" class="contact-link wa">💬 WhatsApp</a>
                    <a href="https://t.me/{phone}" target="_blank" class="contact-link tg">✈️ Telegram</a>
                """, unsafe_allow_html=True)
            
            if pd.notnull(row.get('E-mail')):
                st.caption(row['E-mail'])

except Exception as e:
    st.error(f"Ошибка: {e}")

# Правильная легенда
st.sidebar.header("🏢 Подразделения")
st.sidebar.markdown("""
- **001**: Администрация
- **002**: Отдел ВЭД
- **003**: Ветпрепараты
- **004**: Агропродукты
- **005**: Сырье и корма
- **006**: Кадры / Право
- **007**: Финансы
- **008**: Хоз. служба
""")
