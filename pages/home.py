import streamlit as st
from data import ouvrir_inventaire, ouvrir_organisation, organisation_to_dict
from utils import metric_card

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
        "pourcentage",
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
        df_rh["nb_sans_suppleant"] = df_rh["sans_suppleant"].astype(int)

        rh_division = (
            df_rh.groupby("division", dropna=False)
            .agg(
                nb_competences=("noeud", "count"),
                nb_sans_suppleant=("nb_sans_suppleant", "sum"),
            )
            .reset_index()
        )

        rh_division["taux_sans_suppleant"] = (
            rh_division["nb_sans_suppleant"] / rh_division["nb_competences"]
        ).round(3)
        rh_departement = (
            df_rh.groupby(["division", "departement"], dropna=False)
            .agg(
                nb_competences=("noeud", "count"),
                nb_sans_suppleant=("nb_sans_suppleant", "sum"),
            )
            .reset_index()
        )

        rh_departement["taux_sans_suppleant"] = (
            rh_departement["nb_sans_suppleant"] / rh_departement["nb_competences"]
        ).round(3)

        st.subheader("Vision globale RH")

        c1, c2, c3 = st.columns(3)
        c1.metric("Compétences totales", int(len(df_rh)), border=True)
        c2.metric("Sans suppléant", int(df_rh["nb_sans_suppleant"].sum()), border=True)
        c3.metric(
            "Taux sans suppléant",
            f"{(df_rh['nb_sans_suppleant'].sum() / len(df_rh) * 100):.1f} %",
            border=True,
        )

        st.markdown("### Par division")
        st.dataframe(rh_division, use_container_width=True, hide_index=True)

        st.markdown("### Par département")
        st.dataframe(rh_departement, use_container_width=True, hide_index=True)
