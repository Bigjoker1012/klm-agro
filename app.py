import streamlit as st
import pandas as pd

# Настройка страницы
st.set_page_config(page_title="КЛМ Справочник", layout="wide")

# Функция для конвертации ссылок Google Drive в прямые ссылки на картинки
def fix_drive_url(url):
    if pd.isna(url) or 'drive.google.com' not in str(url):
        return "https://via.placeholder.com/150?text=No+Photo"
    file_id = url.split('/')[-2] if '/view' in url else url.split('=')[-1]
    return f"https://drive.google.com/uc?export=view&id={file_id}"

# 1. Подключаемся к твоей таблице
SHEET_URL = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"

@st.cache_data(ttl=600) # Обновлять данные каждые 10 минут
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    
    st.title("🧬 Интерактивный Справочник КЛМ")
    st.write("Привет, Андрюша! Твоя база на 56 человек готова к работе.")

    # 2. Поиск
    search = st.text_input("🔍 Кого ищем? (Имя, должность или ID отдела)", "").lower()

    # Фильтрация
    if search:
        mask = df.apply(lambda x: x.astype(str).str.lower().str.contains(search)).any(axis=1)
        display_df = df[mask]
    else:
        display_df = df

    # 3. Рисуем сетку
    cols = st.columns(4) # 4 колонки в ряд

    for i, (_, row) in enumerate(display_df.iterrows()):
        with cols[i % 4]:
            with st.container(border=True):
                # Фото сотрудника
                img_url = fix_drive_url(row['Фото'])
                st.image(img_url, use_container_width=True)
                
                # Данные
                st.subheader(f"{row['Фамилия']} {row['Имя']}")
                st.info(f"📍 {row['Должность']}")
                
                # Кнопки связи
                phone = str(row['Личный телефон']).replace(" ", "").replace("-", "")
                
                c1, c2, c3 = st.columns(3)
                
                # Прямой вызов
                c1.markdown(f"[📞](tel:{phone})", help="Позвонить")
                
                # WhatsApp Web
                c2.markdown(f"[💬](https://web.whatsapp.com/send?phone={phone.replace('+', '')})", help="WhatsApp")
                
                # Telegram
                # Если в будущем добавишь колонку 'TG', заменим phone на ник
                c3.markdown(f"[✈️](https://t.me/{phone})", help="Telegram")
                
                if pd.notnull(row['E-mail']):
                    st.write(f"✉️ {row['E-mail']}")

except Exception as e:
    st.error(f"Ой! Что-то не так с таблицей. Проверь доступ. Ошибка: {e}")

# Легенда в боковой панели
st.sidebar.header("🏢 Подразделения")
st.sidebar.markdown("""
- **001**: Руководство
- **002**: ВЭД
- **005**: Транспорт
- **008**: Хоз. служба
""")
