import streamlit as st
import pandas as pd

st.set_page_config(page_title="КЛМ Справочник", layout="wide")

def fix_drive_url(url):
    if pd.isna(url) or 'drive.google.com' not in str(url):
        return "https://via.placeholder.com/150?text=No+Photo"
    try:
        file_id = url.split('/')[-2] if '/view' in url else url.split('=')[-1]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except:
        return "https://via.placeholder.com/150?text=Error"

# Твоя ссылка
SHEET_URL = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip() # Чистим пробелы в названиях
    return df

try:
    df = load_data()
    
    st.title("🧬 Интерактивный Справочник КЛМ")
    
    search = st.text_input("🔍 Поиск по Ф.И.О., должности или ID отдела", "").lower()

    if search:
        mask = df.apply(lambda x: x.astype(str).str.lower().str.contains(search)).any(axis=1)
        display_df = df[mask]
    else:
        display_df = df

    cols = st.columns(4)

    for i, (_, row) in enumerate(display_df.iterrows()):
        with cols[i % 4]:
            with st.container(border=True):
                # Пробуем найти фото (если колонка называется "Фото")
                img_url = fix_drive_url(row.get('Фото', ''))
                st.image(img_url, use_container_width=True)
                
                # Работаем с твоими названиями колонок
                st.subheader(row.get('Ф.И.О.', 'Сотрудник'))
                st.info(f"📍 {row.get('Должность', '-')}")
                st.caption(f"🆔 Отдел: {row.get('ID отдела', '-')}")
                
                # Кнопки связи
                phone = str(row.get('Тел. Личный', '')).replace(" ", "").replace("-", "")
                
                if phone and phone != 'nan':
                    c1, c2, c3 = st.columns(3)
                    # Прямой звонок
                    c1.markdown(f"[📞](tel:{phone})")
                    # WhatsApp (убираем + для ссылки)
                    wa_phone = phone.replace('+', '')
                    c2.markdown(f"[💬](https://web.whatsapp.com/send?phone={wa_phone})")
                    # Telegram
                    c3.markdown(f"[✈️](https://t.me/{phone})")
                
                email = row.get('E-mail', '')
                if pd.notnull(email) and email != 'nan':
                    st.write(f"✉️ {email}")

except Exception as e:
    st.error(f"Ошибка в данных: {e}")

# ТВОЯ ПРАВИЛЬНАЯ ЛЕГЕНДА
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
