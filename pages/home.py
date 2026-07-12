import streamlit as st
from data import ouvrir_inventaire, ouvrir_organisation, organisation_to_dict
from utils import metric_card

user = st.session_state.get("collaborateur_connecte")
rh = st.session_state.get("rh_connecte")

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
        "Secteurs",
        "type",
        "description",
        "titulaire",
        "Suppléant 1",
        "Suppléant 2",
        "status",
    ]
]

if rh:
    tab_collab, tab_manager, tab_RH = st.tabs(
        ["Vue collaborateur", "Vue manager", "Vision RH"]
    )
else:
    tab_collab, tab_manager = st.tabs(["Vue collaborateur", "Vue manager"])

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
