import streamlit as st
from data import ouvrir_collaborateurs

users = ouvrir_collaborateurs().copy()
records = users.to_dict("records")

st.set_page_config(page_title="Gestion de la suppléance", layout="wide")

with st.sidebar:
    st.markdown("## Session")
    st.caption("Simulation du collaborateur connecté")

    selected_user = st.selectbox(
        "Collaborateur",
        options=records,
        format_func=lambda u: u["collaborateur"],
        key="user_connecte",
        placeholder="Choisir un collaborateur",
    )
    st.session_state["collaborateur_connecte"] = selected_user["collaborateur"]
    st.session_state["rh_connecte"] = selected_user["RH"]

    st.divider()


pg = st.navigation(
    [
        st.Page("pages/home.py", title="Home", icon=":material/home:"),
        st.Page(
            "pages/collaborateurs.py", title="Collaborateurs", icon=":material/group:"
        ),
        st.Page("pages/organisation.py", title="Organisation", icon=":material/build:"),
        st.Page("pages/inventaire.py", title="Inventaire", icon=":material/list:"),
    ]
)

pg.run()
