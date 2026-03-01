import streamlit as st
import pandas as pd
import re

# 1. Настройки страницы
st.set_page_config(page_title="КЛМ Справочник", layout="wide")

# 2. Исправленный CSS (учитывает и ПК, и Андроид)
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .block-container { padding: 1rem !important; }
    
    /* Сетка для ПК: по 4 в ряд */
    [data-testid="column"] {
        flex: 1 1 calc(25% - 1rem) !important;
        min-width: 280px !important;
    }

    /* АДАПТИВНОСТЬ ДЛЯ АНДРОИДА: если экран меньше 800px — 1 в ряд */
    @media (max-width: 800px) {
        [data-testid="column"] {
            flex: 1 1 100% !important;
            width: 100% !important;
        }
        .card { min-height: auto !important; margin-bottom: 20px !important; }
    }

    .card {
        background: white; border-radius: 12px; padding: 15px;
        border: 1px solid #e0e0e0; text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 15px; min-height: 415px;
        display: flex; flex-direction: column;
    }
    .img-circle {
        width: 115px; height: 115px; border-radius: 50%;
        object-fit: cover; border: 3px solid #f0f2f5;
        margin: 0 auto 10px auto; display: block;
        background-color: #f8f9fa;
    }
    .name { font-size: 15px; font-weight: bold; margin-bottom: 2px; color: #1e1e1e; min-height: 38px; display: flex; align-items: center; justify-content: center; line-height: 1.2; }
    .job { font-size: 11px; color: #757575; height: 32px; overflow: hidden; margin-bottom: 12px; line-height: 1.2; }
    
    .btn {
        display: block; width: 100%; padding: 8px 0; margin-top: 5px;
        border-radius: 6px; font-size: 13px; font-weight: bold;
        text-decoration: none !important; color: white !important;
        text-align: center; height: 35px; line-height: 20px;
    }
    .b-call { background-color: #007bff; }
    .b-wa { background-color: #28a745; }
    .b-tg { background-color: #0088cc; }
    .b-mail { background-color: #6c757d; }
    .b-none { background-color: #f8f9fa; color: #ced4da !important; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

def get_photo(url):
    placeholder = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    if pd.isna(url) or str(url).strip() == "": return placeholder
    match = re.search(r'[-\w]{25,}', str(url))
    if match:
        return f"https://lh3.googleusercontent.com/d/{match.group()}"
    return placeholder

@st.cache_data(ttl=600)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1nualyTma75WZ4eZlVuPEPMDqz94qmCx5blby-9tZCOU/export?format=csv"
    df = pd.read_csv(url)
    df.columns = [str(c).strip() for c in df.columns]
    if 'ID отдела' in df.columns:
        df['d_id'] = pd.to_numeric(df['ID отдела'], errors='coerce').fillna(0).astype(int)
    return df

try:
    df = load_data()
    
    # Сайдбар
    st.sidebar.title("🏢 Подразделения")
    depts = {
        "Все": 0, "Администрация": 1, "ВЭД": 2, "Ветпрепараты": 3,
        "Агропродукты": 4, "Сырье и корма": 5, "Кадры": 6, "Финансы": 7, "Хоз. служба": 8
    }
    sel = st.sidebar.radio("Показать:", list(depts.keys()))
    search = st.text_input("🔍 Поиск по ФИО или должности", "")

    f_df = df.copy()
    if depts[sel] != 0:
        f_df = f_df[f_df['d_id'] == depts[sel]]
    if search:
        search_lower = search.lower()
        f_df = f_df[f_df['Ф.И.О.'].str.lower().str.contains(search_lower) | 
                    f_df['Должность'].str.lower().str.contains(search_lower)]

    if not f_df.empty:
        f_df = f_df.sort_values('Ф.И.О.')
        for i in range(0, len(f_df), 4):
            cols = st.columns(4)
            batch = f_df.iloc[i:i+4]
            for j, (_, emp) in enumerate(batch.iterrows()):
                with cols[j]:
                    p_val = emp.get('Тел. Личный') if pd.notnull(emp.get('Тел. Личный')) else emp.get('Тел. Рабочий')
                    phone = "".join(filter(str.isdigit, str(p_val)))
                    
                    btns = ""
                    if len(phone) > 5:
                        clean_p = f"+{phone}" if not phone.startswith('375') else phone
                        btns += f'<a href="tel:{clean_p}" class="btn b-call">📞 Позвонить</a>'
                        btns += f'<a href="https://wa.me/{phone}" class="btn b-wa" target="_blank">💬 WhatsApp</a>'
                        btns += f'<a href="https://t.me/+{phone}" class="btn b-tg" target="_blank">✈️ Telegram</a>'
                    else:
                        btns += '<div class="btn b-none">Нет номера</div><div class="btn b-none">—</div><div class="btn b-none">—</div>'

                    email = emp.get('E-mail')
                    if pd.notnull(email) and "@" in str(email):
                        btns += f'<a href="mailto:{email}" class="btn b-mail">✉️ Почта</a>'
                    else:
                        btns += '<div class="btn b-none">Нет почты</div>'

                    st.markdown(f"""
                    <div class="card">
                        <img src="{get_photo(emp.get('Фото'))}" class="img-circle">
                        <div class="name">{emp.get('Ф.И.О.', '---')}</div>
                        <div class="job">{emp.get('Должность', '-')}</div>
                        {btns}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Никого не нашли.")

except Exception as e:
    st.error(f"Техническая ошибка: {e}")
