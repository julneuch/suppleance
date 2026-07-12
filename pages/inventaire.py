import streamlit as st
from data import (
    ecrire_inventaire,
    ouvrir_inventaire,
    ouvrir_collaborateurs,
    organisation_to_dict,
    STATUS,
    TYPES,
)

collaborateur_connecte = st.session_state["collaborateur_connecte"]

st.markdown("""
    # Gestion de l'inventaire des connaissances et savoir-faire
    Cette page permet de gérer des connaissances et savoir-faire, ainsi que leurs titulaires et suppléants.
    """)

collaborateurs = ouvrir_collaborateurs()["collaborateur"].tolist()
inventaire = ouvrir_inventaire()

noeuds = organisation_to_dict()


def label_noeud(noeud_id: int) -> str:
    return noeuds[noeud_id]


selected_id = st.selectbox(
    "Sélectionne un noeud",
    options=list(noeuds.keys()),  # valeurs retournées = ids
    format_func=label_noeud,  # affichage = label humain
)

inventaire_filtre = inventaire[inventaire["noeud"] == selected_id]

edited_df = st.data_editor(
    inventaire_filtre,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    column_config={
        "titulaire": st.column_config.SelectboxColumn(
            "Titulaire",
            help="Choisis le titulaire du noeud",
            width="medium",
            options=collaborateurs,
            required=True,
        ),
        "Suppléant 1": st.column_config.SelectboxColumn(
            "Suppléant 1",
            help="Choisis le suppléant 1 du noeud",
            width="medium",
            options=collaborateurs,
            required=False,
        ),
        "Suppléant 2": st.column_config.SelectboxColumn(
            "Suppléant 2",
            help="Choisis le suppléant 2 du noeud",
            width="medium",
            options=collaborateurs,
            required=False,
        ),
        "type": st.column_config.SelectboxColumn(
            "Type",
            help="Choisis le type ",
            width="medium",
            options=TYPES,
            required=True,
        ),
        "status": st.column_config.SelectboxColumn(
            "Status",
            help="Choisis le statut",
            width="medium",
            options=STATUS,
            required=True,
            default="Inactif",
        ),
        "noeud": st.column_config.NumberColumn(
            "Noeud",
            default=selected_id,
            disabled=True,
        ),
        "description": st.column_config.TextColumn(
            "Description",
            help="Description de la connaissance ou du savoir-faire",
            width="large",
            required=True,
        ),
    },
)


if st.button("Enregistrer"):
    inventaire_maj = inventaire.copy()
    inventaire_maj = inventaire_maj[inventaire_maj["noeud"] != selected_id]
    inventaire_maj = __import__("pandas").concat(
        [inventaire_maj, edited_df], ignore_index=True
    )
    ecrire_inventaire(inventaire_maj)
    st.success("Inventaire enregistré.")
