import streamlit as st
import pandas as pd

from data import (
    ouvrir_organisation,
    ecrire_organisation,
    ouvrir_collaborateurs_managers,
    ouvrir_collaborateurs,
)

st.markdown("""
    # Gestion de l'organisation
    Cette page permet de gérer l'organisation et ses différentes structures.
    """)

orga = ouvrir_organisation()

selected_division = st.selectbox(
    "Sélectionne une division",
    options=list(orga["division"].unique()),  # valeurs retournées = ids
)

managers = ouvrir_collaborateurs_managers()
managers = managers.merge(orga, left_on="noeud", right_on="id", how="left")
managers = managers[managers["division"] == selected_division]
managers = managers[["collaborateur", "division"]]
managers = managers["collaborateur"].tolist()


if selected_division:

    orga_filtre = orga[orga["division"] == selected_division]

    edited_df = st.data_editor(
        orga_filtre,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "responsable": st.column_config.SelectboxColumn(
                "Responsable",
                help="Choisis le responsable du noeud",
                width="medium",
                options=managers,
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

    if st.button("Enregistrer"):
        orga_maj = orga.copy()
        orga_maj = orga_maj[orga_maj["division"] != selected_division]
        orga_maj = __import__("pandas").concat([orga_maj, df], ignore_index=True)
        ecrire_organisation(orga_maj)
        st.success("Organisation enregistrée.")
