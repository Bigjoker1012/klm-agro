import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="КЛМ Справочник", layout="wide")

# Ультра-компактный CSS: убираем всё лишнее
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .block-container { padding: 1rem !important; }
    [data-testid="stVerticalBlock"] > div { gap: 0rem !important; }
    
    .card {
        background: white; border-radius: 12px; padding: 15px;
        border: 1px solid #e0e0e0; text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 15px; min-height: 420px;
    }
    .img-circle {
        width: 120px; height: 120px; border-radius: 50%;
        object-fit: cover; border: 3px solid #f0f2f5;
        margin: 0 auto 10px auto; display: block;
    }
    .name { font-size: 16px; font-weight: bold; margin-bottom: 2px; color: #1e1e1e; }
    .job { font-size: 12px; color: #757575; height: 32px; overflow: hidden; margin-bottom: 12px; }
    
    .btn {
        display: block; width: 100%; padding: 8px 0; margin-top: 6px;
        border-radius: 6px; font-size: 13px; font-weight: bold;
        text-decoration: none !important; color: white !important;
        text-align: center; height: 35px; line-height: 19px;
    }
    .b-call { background-color: #007bff; }
    .b-wa { background-color: #28a745; }
    .b-tg { background-color: #0088cc; }
    .b-mail { background-color: #6c757d; }
    .b-none { background-color: #f8f9fa; color: #adb5bd !important; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

def get_photo(url):
    # Если в таблице пусто — даем заглушку
    if pd.isna(url) or str(url).strip() == "":
        return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    # Вырезаем ID и делаем прямую ссылку
    match = re.search(r'[-\w]{25,}', str(url))
    if match:
        return f"https://drive.google.com/uc?export=view&id={match.group()}"
    return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

@st.cache_data(ttl=0)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"
    df = pd.read_csv(url)
    df.columns = [str(c).strip() for c in df.columns]
    # Чистим ID отделов
    if 'ID отдела' in df.columns:
        df['d_id'] = pd.to_numeric(df['ID отдела'], errors='coerce').fillna(0).astype(int)
    return df

try:
    df = load_data()
    
    # Сайдбар
    depts = {
        "Все": 0, "Администрация": 1, "ВЭД": 2, "Ветпрепараты": 3,
        "Агропродукты": 4, "Сырье и корма": 5, "Кадры": 6, "Финансы": 7, "Хоз. служба": 8
    }
    sel = st.sidebar.radio("Отделы:", list(depts.keys()))
    search = st.text_input("🔍 Поиск", "")

    # Фильтрация
    f_df = df.copy()
    if depts[sel] != 0:
        f_df = f_df[f_df['d_id'] == depts[sel]]
    if search:
        f_df = f_df[f_df.apply(lambda x: x.astype(str).str.lower().str.contains(search.lower())).any(axis=1)]

    # Отрисовка сетки по 4 в ряд
    if not f_df.empty:
        f_df = f_df.sort_values('Ф.И.О.')
        for i in range(0, len(f_df), 4):
            cols = st.columns(4)
            batch = f_df.iloc[i:i+4]
            for j, (_, emp) in enumerate(batch.iterrows()):
                with cols[j]:
                    # Формируем кнопки
                    p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                    phone = "".join(filter(str.isdigit, str(p_val)))
                    
                    btn_html = ""
                    if len(phone) > 5:
                        btn_html += f'<a href="tel:+{phone}" class="btn b-call">📞 Позвонить</a>'
                        btn_html += f'<a href="https://wa.me/{phone}" class="btn b-wa">💬 WhatsApp</a>'
                        btn_html += f'<a href="https://t.me/+{phone}" class="btn b-tg">✈️ Telegram</a>'
                    else:
                        btn_html += '<div class="btn b-none">Нет номера</div><div class="btn b-none">—</div><div class="btn b-none">—</div>'

                    email = emp.get('E-mail')
                    if pd.notnull(email) and "@" in str(email):
                        btn_html += f'<a href="mailto:{email}" class="btn b-mail">✉️ Почта</a>'
                    else:
                        btn_html += '<div class="btn b-none">Нет почты</div>'

                    # Сама карточка
                    st.markdown(f"""
                    <div class="card">
                        <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                        <div class="name">{emp.get('Ф.И.О.', '---')}</div>
                        <div class="job">{emp.get('Должность', '-')}</div>
                        {btn_html}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("Никого не нашли")

except Exception as e:
    st.error(f"Ошибка: {e}")
