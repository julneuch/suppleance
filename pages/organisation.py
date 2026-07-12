import streamlit as st
import pandas as pd

from data import ouvrir_organisation, ecrire_organisation, ouvrir_collaborateurs

st.markdown("""
    # Gestion de l'organisation
    Cette page permet de gérer l'organisation et ses différentes structures.
    """)

collaborateurs = ouvrir_collaborateurs()["collaborateur"].tolist()
st.session_state.orga = ouvrir_organisation()


edited_df = st.data_editor(
    st.session_state.orga,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    column_config={
        "responsable": st.column_config.SelectboxColumn(
            "Responsable",
            help="Choisis le responsable du noeud",
            width="medium",
            options=collaborateurs,
            required=True,
        ),
    },
    disabled=["id"],
)

df = edited_df.copy()

if "id" in df.columns:
    max_id = df["id"].max()
    if pd.isna(max_id):
        max_id = 0
    mask_new = df["id"].isna()
    nb_new = mask_new.sum()
    if nb_new > 0:
        df.loc[mask_new, "id"] = range(int(max_id) + 1, int(max_id) + 1 + nb_new)
        df["id"] = df["id"].astype(int)

st.session_state.orga = df

ecrire_organisation(st.session_state.orga)
