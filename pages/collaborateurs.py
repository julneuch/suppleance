import streamlit as st
from data import *

st.markdown("""
    # Gestion des collaborateurs
    Cette page permet de gérer les collaborateurs et leurs dates d'entrée et de sortie.
    """)

collaborateurs = ouvrir_collaborateurs()


edited_df = st.data_editor(
    collaborateurs,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    column_config={
        "division": st.column_config.SelectboxColumn(
            "Division",
            help="Choisis la division du collaborateur",
            width="medium",
            options=DIVISION,
            required=True,
        ),
    },
)
ecrire_collaborateurs(edited_df)
