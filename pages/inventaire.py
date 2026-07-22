import streamlit as st
from data import (
    CARACTERE,
    NATURES,
    ecrire_inventaire,
    ouvrir_inventaire,
    ouvrir_collaborateurs,
    organisation_to_dict,
    STATUS,
    ouvrir_organisation,
)

collaborateur_connecte = st.session_state["collaborateur_connecte"]

st.markdown("""
    # Gestion de l'inventaire des connaissances et savoir-faire
    Cette page permet de gérer des connaissances et savoir-faire, ainsi que leurs titulaires et suppléants.
    """)


inventaire = ouvrir_inventaire()
collabs = ouvrir_collaborateurs()
orga = ouvrir_organisation()

noeuds = organisation_to_dict(user=collaborateur_connecte)


def label_noeud(noeud_id: int) -> str:
    return noeuds[noeud_id]


selected_id = st.selectbox(
    "Sélectionne un noeud",
    options=list(noeuds.keys()),  # valeurs retournées = ids
    format_func=label_noeud,  # affichage = label humain
)

if selected_id:

    inventaire_filtre = inventaire[inventaire["noeud"] == selected_id]
    collaborateurs_filtre = collabs[
        collabs["division"] == orga.loc[orga["id"] == selected_id, "division"].values[0]
    ]

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
                options=collaborateurs_filtre["collaborateur"].tolist(),
                required=True,
            ),
            "Suppléant 1": st.column_config.SelectboxColumn(
                "Suppléant 1",
                help="Choisis le suppléant 1 du noeud",
                width="medium",
                options=collaborateurs_filtre["collaborateur"].tolist(),
                required=False,
            ),
            "Suppléant 2": st.column_config.SelectboxColumn(
                "Suppléant 2",
                help="Choisis le suppléant 2 du noeud",
                width="medium",
                options=collaborateurs_filtre["collaborateur"].tolist(),
                required=False,
            ),
            "nature": st.column_config.SelectboxColumn(
                "Nature de la compétence",
                help="Choisis la nature de la compétence",
                width="medium",
                options=NATURES,
                required=True,
            ),
            "caractère": st.column_config.SelectboxColumn(
                "Caractère de la compétence",
                help="Choisis le caractère de la compétence",
                width="medium",
                options=CARACTERE,
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
            "pourcentage": st.column_config.NumberColumn(
                "Pourcentage",
                help="Pourcentage de maîtrise de la compétence",
                min_value=0,
                max_value=100,
                step=1,
                format="%d%%",
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

else:
    st.warning("L'utilisateur n'est pas responsable d'un noeud.")
