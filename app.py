import streamlit as st
import pandas as pd

st.set_page_config(page_title="КЛМ Справочник", layout="wide")

st.markdown("""
    <style>
    .employee-card {
        background-color: white; border-radius: 12px; padding: 15px;
        border: 1px solid #ddd; text-align: center; margin-bottom: 20px;
    }
    .contact-btn {
        display: block; padding: 8px; color: white !important;
        text-decoration: none; border-radius: 5px; margin-top: 5px; font-size: 13px;
    }
    .btn-call { background-color: #007bff; }
    .btn-wa { background-color: #25d366; }
    .btn-tg { background-color: #0088cc; }
    </style>
    """, unsafe_allow_html=True)

def fix_drive_url(url):
    if pd.isna(url) or 'drive.google.com' not in str(url):
        return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    file_id = url.split('/')[-2] if '/view' in url else url.split('=')[-1]
    return f"https://drive.google.com/uc?export=view&id={file_id}"

SHEET_URL = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"

@st.cache_data(ttl=10) # Обновляем часто для теста
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = [str(c).strip() for c in df.columns] # Чистим заголовки
    return df

try:
    df = load_data()
    
    # АВТО-ОПРЕДЕЛЕНИЕ КОЛОНОК (чтобы не ошибиться)
    col_fio = next((c for c in df.columns if 'Ф.И.О' in c or 'ФИО' in c), None)
    col_phone = next((c for c in df.columns if 'Тел' in c or 'телефон' in c.lower()), None)
    col_job = next((c for c in df.columns if 'Должность' in c), None)
    col_photo = next((c for c in df.columns if 'Фото' in c), None)
    col_dept = next((c for c in df.columns if 'отдел' in c.lower()), None)

    st.title("🧬 Справочник КЛМ")
    
    search = st.text_input("🔍 Поиск", "")
    if search:
        df = df[df.apply(lambda x: x.astype(str).str.lower().str.contains(search.lower())).any(axis=1)]

    # Вывод карточек
    cols = st.columns(4)
    for i, (_, emp) in enumerate(df.iterrows()):
        with cols[i % 4]:
            st.markdown('<div class="employee-card">', unsafe_allow_html=True)
            
            # Фото
            photo_url = fix_drive_url(emp.get(col_photo))
            st.image(photo_url, use_container_width=True)
            
            # Данные
            st.markdown(f"**{emp.get(col_fio, 'ФИО не найдено')}**")
            st.caption(f"{emp.get(col_job, '-')}")
            
            # Кнопки связи
            raw_phone = str(emp.get(col_phone, ''))
            phone = "".join(filter(str.isdigit, raw_phone)) # Только цифры
            
            if len(phone) > 5:
                # Если номер начинается на 80, меняем на 375 для WA
                wa_phone = phone if phone.startswith('375') else '375' + phone[1:] if phone.startswith('80') else phone
                st.markdown(f"""
                    <a href="tel:+{phone}" class="contact-btn btn-call">📞 Позвонить</a>
                    <a href="https://wa.me/{wa_phone}" target="_blank" class="contact-btn btn-wa">💬 WhatsApp</a>
                    <a href="https://t.me/+{phone}" target="_blank" class="contact-btn btn-tg">✈️ Telegram</a>
                """, unsafe_allow_html=True)
            else:
                st.write("⚠️ Нет номера")
                
            st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка: {e}. Проверь таблицу!")

st.sidebar.markdown("### Легенда")
st.sidebar.info("001 Администрация\n002 ВЭД\n003 Ветпрепараты\n004 Агропродукты...")
