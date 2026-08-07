import streamlit as st
import pandas as pd
from data import (
    CARACTERE,
    NATURES,
    ecrire_inventaire,
    ouvrir_inventaire,
    ouvrir_collaborateurs,
    STATUS,
    TEMPO,
    ouvrir_organisation,
)

collaborateur_connecte = st.session_state["collaborateur_connecte"]

st.markdown("""
    # Identification par les collaborateurs des compétences
    Cette page permet aux collaborateurs d'identifier directement les connaissances et savoirs-faires qu'il détiennent et qu'ils jugent sont uniques ou rares dans l'organisation.
    """)


inventaire = ouvrir_inventaire()
# Id technique si absent
if "id_ligne" not in inventaire.columns:
    inventaire = inventaire.reset_index(drop=True)
    inventaire["id_ligne"] = inventaire.index.astype(str)

collabs = ouvrir_collaborateurs()

orga = ouvrir_organisation()

collabs = collabs.merge(orga, left_on="noeud", right_on="id", how="left")

user = collabs[collabs["collaborateur"] == collaborateur_connecte].copy()
selected_id = user["noeud"].values[0]


if selected_id:
    st.markdown("""
    ### Compétence ou je suis déjà identifié comme titulaire ou suppléant.
    """)
    inventaire_filtre = inventaire[
        inventaire["titulaire"].eq(collaborateur_connecte)
        | inventaire["Suppléant 1"].eq(collaborateur_connecte)
        | inventaire["Suppléant 2"].eq(collaborateur_connecte)
    ]

    collaborateurs_filtre = collabs[
        collabs["division"] == orga.loc[orga["id"] == selected_id, "division"].values[0]
    ]

    affichage_df = inventaire_filtre[
        [
            "id_ligne",
            "titulaire",
            "description",
            "nature",
            "caractère",
            "status",
            "tempo",
            "Suppléant 1",
            "Suppléant 2",
            # "noeud",
            "documentation",
        ]
    ].copy()

    event = st.dataframe(
        affichage_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={"id_ligne": None},
    )

    selected_rows = event.selection.rows

    # Gestion de la modification des compétences déjà proposées.
    # Seules les compétences avec un statut proposées sont modifiables.
    if selected_rows:
        selected_index = selected_rows[0]
        row = affichage_df.iloc[selected_index]
        selected_row_id = row["id_ligne"]

        st.markdown("### Détail de la ligne sélectionnée")

        if row["status"] != STATUS[2]:
            st.info(
                "Cette ligne est en lecture seule. Seules les lignes au statut 'proposé' peuvent être modifiées."
            )
        else:
            st.markdown("## Modifier la compétence proposée")

            with st.form(f"edit_form_{selected_row_id}"):
                titulaire = st.text_input(
                    "Titulaire", value=row["titulaire"], disabled=True
                )

                description = st.text_area(
                    "Description",
                    value=row["description"] if pd.notna(row["description"]) else "",
                    height=120,
                )

                nature = st.selectbox(
                    "Nature de la compétence",
                    options=NATURES,
                    index=(
                        NATURES.index(row["nature"]) if row["nature"] in NATURES else 0
                    ),
                )

                caractere = st.selectbox(
                    "Caractère de la compétence",
                    options=CARACTERE,
                    index=(
                        CARACTERE.index(row["caractère"])
                        if row["caractère"] in CARACTERE
                        else 0
                    ),
                )

                tempo = st.selectbox(
                    "Temporalité de la compétence",
                    options=TEMPO,
                    index=(
                        TEMPO.index(row["tempo"]) if row["tempo"] in CARACTERE else 0
                    ),
                )

                suppleant_1 = st.selectbox(
                    "Suppléant 1",
                    options=[""]
                    + collaborateurs_filtre["collaborateur"].dropna().tolist(),
                    index=(
                        (
                            [""]
                            + collaborateurs_filtre["collaborateur"].dropna().tolist()
                        ).index(row["Suppléant 1"])
                        if pd.notna(row["Suppléant 1"])
                        and row["Suppléant 1"]
                        in (
                            [""]
                            + collaborateurs_filtre["collaborateur"].dropna().tolist()
                        )
                        else 0
                    ),
                )

                suppleant_2 = st.selectbox(
                    "Suppléant 2",
                    options=[""]
                    + collaborateurs_filtre["collaborateur"].dropna().tolist(),
                    index=(
                        (
                            [""]
                            + collaborateurs_filtre["collaborateur"].dropna().tolist()
                        ).index(row["Suppléant 2"])
                        if pd.notna(row["Suppléant 2"])
                        and row["Suppléant 2"]
                        in (
                            [""]
                            + collaborateurs_filtre["collaborateur"].dropna().tolist()
                        )
                        else 0
                    ),
                )

                documentation_text = st.text_area(
                    "Documentation",
                    value=(
                        "\n".join(row["documentation"])
                        if isinstance(row["documentation"], list)
                        else ""
                    ),
                    height=120,
                    help="Une entrée par ligne",
                )
                submit = st.form_submit_button("Enregistrer les modifications")

            if submit:
                inventaire_reload = ouvrir_inventaire().copy()

                if "id_ligne" not in inventaire_reload.columns:
                    inventaire_reload = inventaire_reload.reset_index(drop=True)
                    inventaire_reload["id_ligne"] = inventaire_reload.index.astype(str)

                mask = inventaire_reload["id_ligne"].eq(selected_row_id)

                if not mask.any():
                    st.error("La ligne n'existe plus dans la source.")
                    st.stop()

                statut_actuel = inventaire_reload.loc[mask, "status"].iloc[0]

                if statut_actuel != STATUS[2]:
                    st.warning(
                        "Cette ligne a déjà été modifiée par un autre utilisateur. Recharge la page."
                    )
                    st.stop()

                inventaire_reload.loc[mask, "Suppléant 1"] = (
                    suppleant_1 if suppleant_1 != "" else None
                )
                inventaire_reload.loc[mask, "Suppléant 2"] = (
                    suppleant_2 if suppleant_2 != "" else None
                )
                inventaire_reload.loc[mask, "nature"] = nature
                inventaire_reload.loc[mask, "caractère"] = caractere
                inventaire_reload.loc[mask, "tempo"] = tempo
                inventaire_reload.loc[mask, "description"] = description
                inventaire_reload.loc[mask, "titulaire"] = collaborateur_connecte
                inventaire_reload.loc[mask, "noeud"] = int(selected_id)

                documentation_list = [
                    line.strip()
                    for line in documentation_text.split("\n")
                    if line.strip()
                ]
                inventaire_reload.at[
                    inventaire_reload.index[mask][0], "documentation"
                ] = documentation_list

                ecrire_inventaire(inventaire_reload)
                st.success("Compétence mise à jour.")
                st.rerun()

    # Saisie des nouvelles compétences proposées par le collaborateur
st.markdown("## Proposer une nouvelle compétence")

options_collaborateurs = [""] + collaborateurs_filtre["collaborateur"].dropna().tolist()
with st.expander("Ajouter une nouvelle compétence", expanded=False):
    with st.form("new_competence_form", clear_on_submit=True):
        titulaire_new = st.text_input(
            "Titulaire",
            value=collaborateur_connecte,
            disabled=True,
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

        suppleant_2_new = st.selectbox(
            "Suppléant 2",
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
            line.strip() for line in documentation_text_new.split("\n") if line.strip()
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
            "Suppléant 2": suppleant_2_new if suppleant_2_new != "" else None,
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
