import streamlit as st
from data import ouvrir_collaborateurs, get_inventaire_propose


def circled_number_black(n: int) -> str:
    if n > 10:
        n = 10
    black = {
        0: "",
        1: "1️⃣",
        2: "2️⃣",
        3: "3️⃣",
        4: "4️⃣",
        5: "5️⃣",
        6: "6️⃣",
        7: "7️⃣",
        8: "8️⃣",
        9: "9️⃣",
        10: "🔟",
    }
    return black.get(n, f"({n})")


users = ouvrir_collaborateurs().copy()
records = users.to_dict("records")

st.set_page_config(page_title="Gestion de la suppléance", layout="wide")

with st.sidebar:
    st.markdown("## Session")
    st.caption("Simulation du collaborateur connecté")

    selected_user = st.selectbox(
        "Collaborateur",
        options=records,
        format_func=lambda u: (
            f"🧑‍💼 {u['collaborateur']}"
            if u.get("Manager") and u.get("RH")
            else (
                f"👔 {u['collaborateur']}"
                if u.get("Manager")
                else f"🧭 {u['collaborateur']}" if u.get("RH") else u["collaborateur"]
            )
        ),
        key="user_connecte",
        placeholder="Choisir un collaborateur",
    )
    st.session_state["collaborateur_connecte"] = selected_user["collaborateur"]
    st.session_state["rh_connecte"] = selected_user["RH"]
    st.session_state["manager_connecte"] = selected_user["Manager"]

    st.divider()

propals = get_inventaire_propose(st.session_state["collaborateur_connecte"])

pg = st.navigation(
    {
        "Home": [
            st.Page("pages/home.py", title="Home", icon=":material/home:"),
        ],
        "Orga Banque": [
            st.Page(
                "pages/collaborateurs.py",
                title="Collaborateurs",
                icon=":material/group:",
            ),
            st.Page(
                "pages/organisation.py", title="Organisation", icon=":material/build:"
            ),
        ],
        "Saisie": [
            st.Page(
                "pages/saisie_collab.py",
                title="Saisie Collaborateur",
                icon=":material/edit:",
            ),
            st.Page(
                "pages/inventaire.py",
                title=f"Inventaire Manager {circled_number_black(len(propals))}",
                icon=":material/list:",
            ),
        ],
    }
)

pg.run()
