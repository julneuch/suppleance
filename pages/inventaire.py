import streamlit as st
import pandas as pd
from data import (
    CARACTERE,
    NATURES,
    DELAI,
    TEMPO,
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
collabs = collabs.merge(orga, left_on="noeud", right_on="id", how="left")

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
        column_order=[
            "status",
            # "delai",
            "titulaire",
            "description",
            "nature",
            "caractère",
            "tempo",
            "Suppléant 1",
            # "Suppléant 2",
            "documentation",
        ],
        column_config={
            "titulaire": st.column_config.SelectboxColumn(
                "Titulaire",
                help="Choisis le titulaire du noeud",
                # width="medium",
                options=collaborateurs_filtre["collaborateur"].tolist(),
                required=True,
            ),
            "Suppléant 1": st.column_config.SelectboxColumn(
                "Suppléant 1",
                help="Choisis le suppléant 1 du noeud",
                # width="medium",
                options=collaborateurs_filtre["collaborateur"].tolist(),
                required=False,
            ),
            "Suppléant 2": st.column_config.SelectboxColumn(
                "Suppléant 2",
                help="Choisis le suppléant 2 du noeud",
                # width="medium",
                options=collaborateurs_filtre["collaborateur"].tolist(),
                required=False,
            ),
            "nature": st.column_config.SelectboxColumn(
                "Nature de la compétence",
                help="Choisis la nature de la compétence",
                # width="medium",
                options=NATURES,
                required=True,
            ),
            "caractère": st.column_config.SelectboxColumn(
                "Caractère de la compétence",
                help="Choisis le caractère de la compétence",
                # width="medium",
                options=CARACTERE,
                required=True,
            ),
            "status": st.column_config.SelectboxColumn(
                "Status",
                help="Choisis le statut",
                # width="medium",
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
            "delai": st.column_config.SelectboxColumn(
                "Délai",
                help="Choisis le délai",
                # width="medium",
                options=DELAI,
                default=None,
            ),
            "tempo": st.column_config.SelectboxColumn(
                "Temporalité",
                help="Choisis la temporalité",
                # width="medium",
                options=TEMPO,
                default=None,
            ),
        },
    )

    if st.button("Enregistrer"):

        max_id = pd.to_numeric(inventaire["id_ligne"], errors="coerce").max()
        max_id = 0 if pd.isna(max_id) else int(max_id)
        masque_id_null = edited_df["id_ligne"].isna() | (edited_df["id_ligne"] == "")
        nb_nouveaux = masque_id_null.sum()
        if nb_nouveaux > 0:
            edited_df.loc[masque_id_null, "id_ligne"] = range(
                max_id + 1,
                max_id + 1 + nb_nouveaux,
            )
        edited_df["noeud"] = int(selected_id)

        inventaire_maj = inventaire.copy()
        inventaire_maj = inventaire_maj[inventaire_maj["noeud"] != selected_id]
        inventaire_maj = __import__("pandas").concat(
            [inventaire_maj, edited_df], ignore_index=True
        )
        ecrire_inventaire(inventaire_maj)
        st.success("Inventaire enregistré.")

    options_collaborateurs = [""] + collaborateurs_filtre[
        "collaborateur"
    ].dropna().tolist()
    with st.expander("Ajouter une nouvelle compétence", expanded=False):
        with st.form("new_competence_form", clear_on_submit=True):
            titulaire_new = st.selectbox(
                "Titulaire",
                options=options_collaborateurs,
                index=0,
            )

            description_new = st.text_area(
                "Description",
                height=120,
                help="Décris la connaissance ou le savoir-faire",
            )

            nature_new = st.selectbox(
                "Nature de la compétence",
                options=NATURES,
                index=0,
            )

            caractere_new = st.selectbox(
                "Caractère de la compétence",
                options=CARACTERE,
                index=0,
            )

            tempo_new = st.selectbox(
                "Temporalité de la compétence",
                options=TEMPO,
                index=0,
            )

            suppleant_1_new = st.selectbox(
                "Suppléant 1",
                options=options_collaborateurs,
                index=0,
            )

            documentation_text_new = st.text_area(
                "Documentation",
                height=120,
                help="Une entrée par ligne",
            )

            submit_new = st.form_submit_button("Enregistrer la nouvelle compétence")

        if submit_new:
            if not description_new.strip():
                st.warning("La description est obligatoire.")
                st.stop()

            inventaire_reload = ouvrir_inventaire().copy()

            if "id_ligne" not in inventaire_reload.columns:
                inventaire_reload = inventaire_reload.reset_index(drop=True)
                inventaire_reload["id_ligne"] = inventaire_reload.index.astype(str)

            max_id = pd.to_numeric(inventaire_reload["id_ligne"], errors="coerce").max()
            max_id = 0 if pd.isna(max_id) else int(max_id)

            documentation_list = [
                line.strip()
                for line in documentation_text_new.split("\n")
                if line.strip()
            ]

            nouvelle_ligne = {
                "id_ligne": str(max_id + 1),
                "status": STATUS[2],
                "titulaire": collaborateur_connecte,
                "description": description_new.strip(),
                "nature": nature_new,
                "caractère": caractere_new,
                "tempo": tempo_new,
                "Suppléant 1": suppleant_1_new if suppleant_1_new != "" else None,
                "documentation": documentation_list,
                "noeud": int(selected_id),
            }

            inventaire_maj = pd.concat(
                [inventaire_reload, pd.DataFrame([nouvelle_ligne])],
                ignore_index=True,
            )

            ecrire_inventaire(inventaire_maj)
            st.success("Nouvelle compétence enregistrée.")
            st.rerun()

else:
    st.warning("L'utilisateur n'est pas responsable d'un noeud.")
