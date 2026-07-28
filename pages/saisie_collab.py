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

    # Saisie des nouvelles comptences proposées
    # par le collab
    st.markdown("""
    ## Proposer une nouvelle compétence :
    """)

    empty_df = inventaire.head(0).copy()
    print(empty_df.dtypes)
    edited_df = st.data_editor(
        empty_df,
        use_container_width=True,
        width="stretch",
        num_rows="dynamic",
        hide_index=True,
        column_order=[
            "status",
            "titulaire",
            "description",
            "nature",
            "caractère",
            "tempo",
            "Suppléant 1",
            "Suppléant 2",
            "documentation",
        ],
        column_config={
            "titulaire": st.column_config.SelectboxColumn(
                "Titulaire",
                help="Choisis le titulaire du noeud",
                # width="medium",
                options=collaborateurs_filtre["collaborateur"].tolist(),
                required=True,
                disabled=True,
                default=collaborateur_connecte,
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
            "tempo": st.column_config.SelectboxColumn(
                "Temporalité",
                help="Choisis la temporalité de la compétence",
                # width="medium",
                options=TEMPO,
                required=True,
            ),
            "status": st.column_config.SelectboxColumn(
                "Status",
                help="Choisis le statut",
                # width="medium",
                options=STATUS,
                required=True,
                default=STATUS[2],
                disabled=True,
            ),
            "noeud": st.column_config.NumberColumn(
                "Noeud",
                default=int(selected_id),
                disabled=True,
            ),
            "documentation": st.column_config.ListColumn(
                "Documentation", required=False
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

        max_id = pd.to_numeric(inventaire["id_ligne"], errors="coerce").max()
        max_id = 0 if pd.isna(max_id) else int(max_id)

        edited_df["noeud"] = int(selected_id)
        edited_df["id_ligne"] = range(max_id + 1, max_id + 1 + len(edited_df))
        inventaire_maj = inventaire.copy()

        inventaire_maj = pd.concat(
            [inventaire_maj, edited_df],
            ignore_index=True,
        )
        ecrire_inventaire(inventaire_maj)
        st.success("Inventaire enregistré.")
