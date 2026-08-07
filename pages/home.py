import streamlit as st
from data import ouvrir_inventaire, ouvrir_organisation, organisation_to_dict
from utils import metric_card
import plotly.express as px
import pandas as pd

user = st.session_state.get("collaborateur_connecte")
rh = st.session_state.get("rh_connecte")
manager = st.session_state.get("manager_connecte")

st.title("Home")
st.caption("Vue synthétique de la suppléance pour l'utilisateur connecté")

if not user:
    st.warning("Aucun collaborateur connecté sélectionné dans la barre latérale.")
    st.stop()

inventaire = ouvrir_inventaire().copy()
organisation = ouvrir_organisation().copy()

# Harmonisation simple des valeurs texte
for col in ["titulaire", "Suppléant 1", "Suppléant 2", "noeud"]:
    if col in inventaire.columns:
        inventaire[col] = inventaire[col].astype(str).fillna("")

if "responsable" in organisation.columns:
    organisation["responsable"] = organisation["responsable"].astype(str).fillna("")
if "id" in organisation.columns:
    organisation["id"] = organisation["id"].astype(str)

user = str(user)

# 1) Nb éléments dont je suis titulaire
nb_titulaire = (inventaire["titulaire"] == user).sum()

# 2) Nb éléments dont je suis suppléant 1 ou 2
nb_suppleant = (
    (inventaire["Suppléant 1"] == user) | (inventaire["Suppléant 2"] == user)
).sum()

# 3) Noeuds dont je suis responsable
noeuds_responsable = (
    organisation.loc[organisation["responsable"] == user, "id"].astype(str).tolist()
)

nb_noeuds_responsable = len(noeuds_responsable)

# 4) Parmi mes noeuds, éléments sans aucun suppléant
inventaire_mes_noeuds = inventaire[
    inventaire["noeud"].astype(str).isin(noeuds_responsable)
].copy()


nb_sans_suppleant = (
    inventaire_mes_noeuds["Suppléant 1"].fillna("").eq("")
    & inventaire_mes_noeuds["Suppléant 2"].fillna("").eq("")
).sum()

mes_noeuds = organisation[organisation["id"].isin(noeuds_responsable)].copy()
inventaire_mes_noeuds = inventaire[inventaire["noeud"].isin(noeuds_responsable)].copy()

nb_elements_mes_noeuds = len(inventaire_mes_noeuds)


elements_sans_suppleant = inventaire_mes_noeuds[
    inventaire_mes_noeuds["Suppléant 1"].fillna("").eq("")
    & inventaire_mes_noeuds["Suppléant 2"].fillna("").eq("")
].copy()


mes_elements = inventaire[
    (inventaire["titulaire"] == user)
    | (inventaire["Suppléant 1"].fillna("").astype(str).str.strip() == user)
    | (inventaire["Suppléant 2"].fillna("").astype(str).str.strip() == user)
].copy()

organisation_dict = organisation_to_dict()

mes_elements["Secteurs"] = mes_elements["noeud"].astype(int).map(organisation_dict)
mes_elements = mes_elements[
    [
        "noeud",
        "nature",
        "caractère",
        "description",
        "titulaire",
        "Suppléant 1",
        "Suppléant 2",
        "status",
        "delai",
        "documentation",
        "update_at",
    ]
]

# Mise en place de la structure des onglets en fonction du rôle de l'utilisateur connecté
if rh:
    if manager:
        tab_collab, tab_manager, tab_RH = st.tabs(
            ["Vue collaborateur", "Vue manager", "Vision RH"]
        )
    else:
        tab_collab, tab_RH = st.tabs(["Vue collaborateur", "Vision RH"])
elif manager:
    tab_collab, tab_manager = st.tabs(["Vue collaborateur", "Vue manager"])
else:
    (tab_collab,) = st.tabs(["Vue collaborateur"])

# Onglet commun à tous les utilisateurs
with tab_collab:
    st.subheader("Mes Compétences")

    c1, c2 = st.columns(2)
    with c1:
        metric_card(
            "👤 Compétences dont je suis titulaire",
            nb_titulaire,
            seuil_orange=None,
            seuil_rouge=None,
        )
    with c2:
        metric_card(
            "🤝 Compétences dont je suis suppléant",
            nb_suppleant,
            seuil_orange=None,
            seuil_rouge=None,
        )

    if not mes_elements.empty:
        mes_elements_graph = inventaire[
            (inventaire["titulaire"] == user)
            | (inventaire["Suppléant 1"].fillna("").astype(str).str.strip() == user)
            | (inventaire["Suppléant 2"].fillna("").astype(str).str.strip() == user)
        ].copy()

        mes_elements_graph["role_utilisateur"] = mes_elements_graph.apply(
            lambda row: (
                "Titulaire" if str(row["titulaire"]).strip() == user else "Suppléant"
            ),
            axis=1,
        )

        df_role = (
            mes_elements_graph.groupby("role_utilisateur", dropna=False)
            .size()
            .reset_index(name="Nombre")
        )

        df_nature = (
            mes_elements_graph["nature"]
            .fillna("Non renseigné")
            .astype(str)
            .str.strip()
            .replace("", "Non renseigné")
            .value_counts(dropna=False)
            .reset_index()
        )
        df_nature.columns = ["Nature", "Nombre"]

        df_caractere = (
            mes_elements_graph["caractère"]
            .fillna("Non renseigné")
            .astype(str)
            .str.strip()
            .replace("", "Non renseigné")
            .value_counts(dropna=False)
            .reset_index()
        )
        df_caractere.columns = ["Caractère", "Nombre"]

        col2, col3 = st.columns(2)

        with col2:
            fig_nature = px.pie(
                df_nature,
                names="Nature",
                values="Nombre",
                hole=0.68,
                color="Nature",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_nature.update_traces(
                textposition="inside",
                texttemplate="%{label}<br>%{percent}",
                insidetextorientation="auto",
            )
            fig_nature.update_layout(
                title="Répartition par nature",
                margin=dict(l=10, r=10, t=50, b=10),
                showlegend=False,
                uniformtext_minsize=12,
                uniformtext_mode="hide",
            )
            st.plotly_chart(fig_nature, use_container_width=True)

        with col3:
            fig_caractere = px.pie(
                df_caractere,
                names="Caractère",
                values="Nombre",
                hole=0.68,
                color="Caractère",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_caractere.update_traces(
                textposition="inside",
                textinfo="label+percent",
                insidetextorientation="horizontal",
            )
            fig_caractere.update_layout(
                title="Répartition par caractère",
                margin=dict(l=10, r=10, t=50, b=10),
                showlegend=False,
            )
            st.plotly_chart(fig_caractere, use_container_width=True)

    else:
        st.info("Aucune donnée disponible pour afficher les graphiques.")

    st.markdown("### Mes compétences concernées")
    if not mes_elements.empty:
        st.dataframe(mes_elements, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune compétence ne vous est actuellement attribuée.")

# Onglet spécifique aux managers
if manager:
    with tab_manager:
        st.subheader("Mes responsabilités organisationnelles")

        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card(
                "🏢 Secteurs dont je suis responsable",
                nb_noeuds_responsable,
                seuil_orange=None,
                seuil_rouge=None,
            )

        with c2:
            metric_card(
                "📚 Compétences unique ou rares identifiées",
                nb_elements_mes_noeuds,
                seuil_orange=None,
                seuil_rouge=None,
            )

        with c3:
            metric_card(
                "⚠️ Compétences sans suppléant sur mes secteurs",
                nb_sans_suppleant,
                seuil_orange=None,
                seuil_rouge=1,
            )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("### Mes noeuds organisationnels")
            if not mes_noeuds.empty:
                st.dataframe(mes_noeuds, use_container_width=True, hide_index=True)
            else:
                st.info("Vous n'êtes responsable d'aucun noeud organisationnel.")

        with col_b:
            st.markdown("### Compétences sans suppléant")
            if not elements_sans_suppleant.empty:
                st.dataframe(
                    elements_sans_suppleant, use_container_width=True, hide_index=True
                )
            else:
                st.success(
                    "Toutes les compétences de vos noeuds ont au moins un suppléant."
                )

# Onglet spécifique aux RH
if rh:
    with tab_RH:
        df_rh = inventaire.merge(
            organisation[["id", "division", "departement", "secteur"]],
            left_on="noeud",
            right_on="id",
            how="left",
        )

        df_rh["sans_suppleant"] = df_rh["Suppléant 1"].fillna("").eq("") & df_rh[
            "Suppléant 2"
        ].fillna("").eq("")

        df_rh["avec_suppleant"] = ~df_rh["sans_suppleant"]

        st.subheader("Vision globale RH")

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "Compétences totales inventoriées ",
                int(len(df_rh)),
                seuil_orange=None,
                seuil_rouge=None,
            )
        with c2:
            metric_card(
                "⚠️ Compétences sans suppléant",
                int(int(df_rh["sans_suppleant"].sum())),
                seuil_orange=None,
                seuil_rouge=1,
            )
        with c3:
            metric_card(
                "⚠️ Taux de compétences sans suppléant",
                float((df_rh["sans_suppleant"].sum() / len(df_rh))),
                seuil_orange=None,
                seuil_rouge=0.000001,
                percent=True,
            )
        # ---------- DIVISIONS ----------
        rh_division = (
            df_rh.groupby("division", dropna=False)
            .agg(
                avec_suppleant=("avec_suppleant", "sum"),
                sans_suppleant=("sans_suppleant", "sum"),
            )
            .reset_index()
        )

        rh_division["nb_competences"] = (
            rh_division["avec_suppleant"] + rh_division["sans_suppleant"]
        )
        rh_division["taux_sans_suppleant"] = (
            rh_division["sans_suppleant"] / rh_division["nb_competences"]
        ).round(3)

        rh_division = rh_division.sort_values(
            ["sans_suppleant", "nb_competences"],
            ascending=[False, False],
        )

        rh_division_long = rh_division.melt(
            id_vars=["division", "nb_competences", "taux_sans_suppleant"],
            value_vars=["avec_suppleant", "sans_suppleant"],
            var_name="statut_suppleance",
            value_name="nb_competences_statut",
        )

        rh_division_long["part"] = (
            rh_division_long["nb_competences_statut"]
            / rh_division_long["nb_competences"]
        )

        rh_division_long["label_barre"] = rh_division_long.apply(
            lambda row: f"{int(row['nb_competences_statut'])} ({row['part']:.0%})",
            axis=1,
        )

        # ---------- DEPARTEMENTS ----------
        rh_departement = (
            df_rh.groupby(["division", "departement"], dropna=False)
            .agg(
                avec_suppleant=("avec_suppleant", "sum"),
                sans_suppleant=("sans_suppleant", "sum"),
            )
            .reset_index()
        )

        rh_departement["nb_competences"] = (
            rh_departement["avec_suppleant"] + rh_departement["sans_suppleant"]
        )
        rh_departement["taux_sans_suppleant"] = (
            rh_departement["sans_suppleant"] / rh_departement["nb_competences"]
        ).round(3)

        rh_departement = rh_departement.sort_values(
            ["sans_suppleant", "nb_competences"],
            ascending=[False, False],
        )

        top10_departement = rh_departement.head(10).copy()
        top10_departement["label_dep"] = (
            top10_departement["division"].fillna("N/A").astype(str)
            + " | "
            + top10_departement["departement"].fillna("N/A").astype(str)
        )

        top10_departement_long = top10_departement.melt(
            id_vars=["label_dep", "nb_competences", "taux_sans_suppleant"],
            value_vars=["avec_suppleant", "sans_suppleant"],
            var_name="statut_suppleance",
            value_name="nb_competences_statut",
        )

        top10_departement_long["part"] = (
            top10_departement_long["nb_competences_statut"]
            / top10_departement_long["nb_competences"]
        )

        top10_departement_long["label_barre"] = top10_departement_long.apply(
            lambda row: f"{int(row['nb_competences_statut'])} ({row['part']:.0%})",
            axis=1,
        )

        col1, col2 = st.columns(2)

        with col1:
            fig_div = px.bar(
                rh_division_long,
                x="# Compétences",
                y="division",
                color="statut_suppleance",
                orientation="h",
                text="label_barre",
                color_discrete_map={
                    "avec_suppleant": "#10b981",
                    "sans_suppleant": "#ef4444",
                },
                category_orders={
                    "statut_suppleance": ["avec_suppleant", "sans_suppleant"]
                },
                custom_data=["nb_competences", "taux_sans_suppleant"],
            )

            fig_div.update_layout(
                title="Ranking des divisions",
                barmode="stack",
                margin=dict(l=10, r=10, t=50, b=10),
                legend_title_text="",
            )

            fig_div.update_traces(
                texttemplate="%{text}",
                textposition="inside",
                insidetextanchor="middle",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Statut : %{fullData.name}<br>"
                    "Nombre : %{x}<br>"
                    "Total compétences : %{customdata[0]}<br>"
                    "Taux sans suppléant : %{customdata[1]:.1%}<extra></extra>"
                ),
            )

            fig_div.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig_div, use_container_width=True)

        with col2:
            fig_dep = px.bar(
                top10_departement_long,
                x="# Compétences",
                y="label_dep",
                color="statut_suppleance",
                orientation="h",
                text="label_barre",
                color_discrete_map={
                    "avec_suppleant": "#10b981",
                    "sans_suppleant": "#ef4444",
                },
                category_orders={
                    "statut_suppleance": ["avec_suppleant", "sans_suppleant"]
                },
                custom_data=["nb_competences", "taux_sans_suppleant"],
            )

            fig_dep.update_layout(
                title="Top 10 départements les plus exposés",
                barmode="stack",
                margin=dict(l=10, r=10, t=50, b=10),
                legend_title_text="",
            )

            fig_dep.update_traces(
                texttemplate="%{text}",
                textposition="inside",
                insidetextanchor="middle",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Statut : %{fullData.name}<br>"
                    "Nombre : %{x}<br>"
                    "Total compétences : %{customdata[0]}<br>"
                    "Taux sans suppléant : %{customdata[1]:.1%}<extra></extra>"
                ),
            )

            fig_dep.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig_dep, use_container_width=True)

        st.markdown("### Par division")
        st.dataframe(rh_division, use_container_width=True, hide_index=True)

        st.markdown("### Par département")
        st.dataframe(rh_departement, use_container_width=True, hide_index=True)
