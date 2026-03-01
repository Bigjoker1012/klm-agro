st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .block-container { padding: 1rem !important; }
    
    /* Основная сетка карточек */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 calc(25% - 1rem) !important; /* На ПК 4 в ряд */
        min-width: 250px !important;
    }

    /* АДАПТИВНОСТЬ ДЛЯ ТЕЛЕФОНА */
    @media (max-width: 640px) {
        [data-testid="column"] {
            flex: 1 1 100% !important; /* На мобилке 1 в ряд */
            min-width: 100% !important;
        }
        .card { 
            min-height: auto !important; 
            margin-bottom: 25px !important; 
        }
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
    }
    .name { font-size: 16px; font-weight: bold; margin-bottom: 2px; color: #1e1e1e; min-height: 38px; display: flex; align-items: center; justify-content: center; line-height: 1.2; }
    .job { font-size: 12px; color: #757575; height: 32px; overflow: hidden; margin-bottom: 12px; line-height: 1.2; }
    
    .btn {
        display: block; width: 100%; padding: 10px 0; margin-top: 6px;
        border-radius: 8px; font-size: 14px; font-weight: bold;
        text-decoration: none !important; color: white !important;
        text-align: center; height: 40px; line-height: 20px;
    }
    .b-call { background-color: #007bff; }
    .b-wa { background-color: #28a745; }
    .b-tg { background-color: #0088cc; }
    .b-mail { background-color: #6c757d; }
    .b-none { background-color: #f8f9fa; color: #ced4da !important; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)
