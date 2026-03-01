import streamlit as st
import pandas as pd

st.set_page_config(page_title="КЛМ Справочник", layout="wide")

# Стили для СОТ и активных кнопок
st.markdown("""
    <style>
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background-color: #f0f2f6;
        clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
        padding: 40px 20px;
        text-align: center;
        transition: 0.3s;
    }
    [data-testid="stVerticalBlock"] > div:hover {
        transform: scale(1.05);
        background-color: #e0e8f0;
    }
    .contact-btn {
        text-decoration: none;
        font-size: 24px;
        margin: 0 10px;
        cursor: pointer !important;
    }
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

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    st.title("🧬 Интерактивный Справочник КЛМ")
    
    search = st.text_input("🔍 Поиск по Ф.И.О., должности или ID отдела", "").lower()
    display_df = df[df.apply(lambda x: x.astype(str).str.lower().str.contains(search)).any(axis=1)] if search else df

    cols = st.columns(4)

    for i, (_, row) in enumerate(display_df.iterrows()):
        with cols[i % 4]:
            # Фото
            img_url = fix_drive_url(row.get('Фото', ''))
            st.image(img_url, use_container_width=True)
            
            # Текст
            st.markdown(f"**{row.get('Ф.И.О.', '')}**")
            st.caption(f"📍 {row.get('Должность', '')}")
            
            # Чистим ID отдела от .0
            dept_id = str(row.get('ID отдела', '')).replace('.0', '').zfill(3)
            st.markdown(f"🆔 Отдел: {dept_id}")
            
            # КНОПКИ (Активные ссылки)
            phone = str(row.get('Тел. Личный', '')).replace(" ", "").replace("-", "")
            if phone and phone != 'nan':
                wa_phone = phone.replace('+', '')
                st.markdown(f"""
                    <div style="display: flex; justify-content: center;">
                        <a href="tel:{phone}" class="contact-btn">📞</a>
                        <a href="https://wa.me/{wa_phone}" target="_blank" class="contact-btn">💬</a>
                        <a href="https://t.me/{phone}" target="_blank" class="contact-btn">✈️</a>
                    </div>
                """, unsafe_allow_html=True)
            
            st.write("---")

except Exception as e:
    st.error(f"Ошибка: {e}")

# Легенда
st.sidebar.header("🏢 Подразделения")
st.sidebar.markdown("""
- **001**: Администрация
- **002**: Отдел ВЭД
- **003**: Отдел ветпрепаратов
- **004**: Отдел агропродуктов
- **005**: Отдел сырья и кормов
- **006**: Правовая и кадровая работа
- **007**: Финансово-экономический
- **008**: Адм.-хозяйственная служба
""")
