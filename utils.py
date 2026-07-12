import streamlit as st


def metric_card(title, value, seuil_orange=None, seuil_rouge=None):
    bg = "#f0f2f6"
    border = "#d9d9d9"
    text = "#111111"

    if seuil_rouge is not None and value >= seuil_rouge:
        bg = "#fdeaea"
        border = "#e74c3c"
        text = "#c0392b"
    elif seuil_orange is not None and value >= seuil_orange:
        bg = "#fff4e5"
        border = "#f39c12"
        text = "#b26a00"

    st.markdown(
        f"""
        <div style="
            background-color:{bg};
            border:1px solid {border};
            border-left:8px solid {border};
            border-radius:12px;
            padding:16px 18px;
            margin:4px 0 8px 0;
        ">
            <div style="font-size:0.95rem; color:#555; margin-bottom:6px;">{title}</div>
            <div style="font-size:2rem; font-weight:700; color:{text};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
