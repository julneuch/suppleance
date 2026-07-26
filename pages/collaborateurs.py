import streamlit as st
from data import *

st.markdown("""
    # Gestion des collaborateurs
    Cette page permet de gérer les collaborateurs et leurs dates d'entrée et de sortie.
    """)

collaborateurs = ouvrir_collaborateurs()
noeuds = organisation_to_dict()


def label_noeud(noeud_id: int) -> str:
    return noeuds[noeud_id]


edited_df = st.data_editor(
    collaborateurs,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    column_config={
        "noeud": st.column_config.SelectboxColumn(
            "Nœud",
            help="Choisis le nœud du collaborateur",
            width="medium",
            options=list(noeuds.keys()),
            format_func=label_noeud,
            required=True,
        ),
    },
)
ecrire_collaborateurs(edited_df)
