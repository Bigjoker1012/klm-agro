import streamlit as st
import pandas as pd

st.set_page_config(page_title="КЛМ Справочник", layout="wide")

# Стиль: Чистые карточки и яркие кнопки
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    .employee-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
        margin-bottom: 20px;
    }
    .btn-container { display: flex; flex-direction: column; gap: 8px; margin-top: 15px; }
    .contact-btn {
        display: block;
        padding: 10px;
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        font-size: 14px;
    }
    .btn-call { background-color: #007bff; }
    .btn-wa { background-color: #25d366; }
    .btn-tg { background-color: #0088cc; }
    </style>
    """, unsafe_allow_html=True)

def fix_drive_url(url):
    if pd.isna(url) or 'drive.google.com' not in str(url):
        return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png" # Иконка юзера
    try:
        file_id = url.split('/')[-2] if '/view' in url else url.split('=')[-1]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except: return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

SHEET_URL = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"

@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    st.title("🧬 Справочник сотрудников КЛМ")
    
    search = st.text_input("🔍 Быстрый поиск (Ф.И.О, отдел, должность)", "")
    
    if search:
        display_df = df[df.apply(lambda x: x.astype(str).str.lower().str.contains(search.lower())).any(axis=1)]
    else:
        display_df = df

    # Сетка: 4 карточки в ряд
    rows = [display_df[i:i + 4] for i in range(0, len(display_df), 4)]

    for row_chunk in rows:
        cols = st.columns(4)
        for i, (_, emp) in enumerate(row_chunk.iterrows()):
            with cols[i]:
                # Сама карточка
                st.markdown('<div class="employee-card">', unsafe_allow_html=True)
                
                # Фото
                img = fix_drive_url(emp.get('Фото', ''))
                st.image(img, use_container_width=True)
                
                # Данные
                st.markdown(f"**{emp.get('Ф.И.О.', '---')}**")
                st.caption(emp.get('Должность', '---'))
                
                dept = str(emp.get('ID отдела', '')).replace('.0', '').zfill(3)
                st.markdown(f"<small>Отдел: {dept}</small>", unsafe_allow_html=True)
                
                # Кнопки
                phone = str(emp.get('Тел. Личный', '')).replace(" ", "").replace("-", "")
                if phone and phone != 'nan' and len(phone) > 5:
                    wa_phone = phone.replace('+', '')
                    st.markdown(f"""
                        <div class="btn-container">
                            <a href="tel:{phone}" class="contact-btn btn-call">📞 Позвонить</a>
                            <a href="https://wa.me/{wa_phone}" target="_blank" class="contact-btn btn-wa">💬 WhatsApp</a>
                            <a href="https://t.me/{phone}" target="_blank" class="contact-btn btn-tg">✈️ Telegram</a>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("📞 Номер не указан")
                
                st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Что-то пошло не так: {e}")

# Легенда
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
