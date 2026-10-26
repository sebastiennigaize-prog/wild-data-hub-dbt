import base64
from pathlib import Path

import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Wild Data Hub | Data Analyst",
    page_icon="🌍",
    layout="wide",
)

GITHUB_URL = "https://github.com/sebastiennigaize-prog/wild-data-hub-dbt"
PDF_PATH = Path(__file__).parent / "dashboard.pdf"


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* Fond adapté au thème Streamlit */
        .stApp {
            background-color: var(--background-color);
        }

        /* Titres adaptés au thème Streamlit */
        h1, h2, h3 {
            color: var(--text-color);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVIGATION
# ============================================================

st.sidebar.title("🌍 Wild Data Hub")

page = st.sidebar.radio(
    "Navigation",
    [
        "Accueil",
        "Dashboard Power BI",
        "Machine Learning",
        "Projet & GitHub",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Projet Data Analyst — Banque mondiale")


# ============================================================
# PAGE 1 — ACCUEIL
# ============================================================

if page == "Accueil":

    st.title("🌍 Wild Data Hub")
    st.subheader("Analyse des indicateurs de développement mondial")

    st.write(
        """
        Wild Data Hub est un projet Data Analyst utilisant les données
        de la Banque mondiale pour analyser les évolutions économiques,
        démographiques, sociales et environnementales à l'échelle
        internationale.

        Le projet combine un pipeline de données automatisé,
        une modélisation analytique, un modèle de Machine Learning
        et un dashboard Power BI.
        """
    )

    st.divider()

    st.header("Architecture du projet")

    st.code(
        """API World Bank
        ↓
Python — Ingestion des données
        ↓
Google BigQuery — Stockage
        ↓
dbt — Transformations et tests
        ↓
Machine Learning — scikit-learn
        ↓
Prédictions enregistrées dans BigQuery
        ↓
Dashboard Power BI""",
        language="text",
    )

    st.header("Technologies utilisées")

    st.write(
        "Python · Google BigQuery · dbt · scikit-learn · "
        "GitHub Actions · Power BI · Streamlit"
    )

    st.link_button(
        "💻 Voir le dépôt GitHub",
        GITHUB_URL,
    )


# ============================================================
# PAGE 2 — DASHBOARD POWER BI
# ============================================================

elif page == "Dashboard Power BI":

    st.title("📊 Dashboard Power BI")

    st.write(
        """
        Ce tableau de bord a été réalisé avec Power BI Desktop
        à partir des données de la Banque mondiale.

        Il comprend six pages consacrées aux indicateurs
        économiques, démographiques, sociaux et environnementaux,
        ainsi qu'aux prédictions du modèle de Machine Learning.
        """
    )

    st.info(
        "Le rapport est présenté dans son format PDF original. "
        "Les filtres Power BI ne sont pas interactifs dans cette version."
    )

    if PDF_PATH.exists():

        pdf_bytes = PDF_PATH.read_bytes()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        pdf_html = f"""
        <iframe
            src="data:application/pdf;base64,{pdf_base64}"
            width="100%"
            height="850"
            style="border:1px solid #dddddd; border-radius:8px;"
            title="Dashboard Power BI Wild Data Hub"
        ></iframe>
        """

        st.markdown(
            pdf_html,
            unsafe_allow_html=True,
        )

        st.download_button(
            label="📥 Télécharger le dashboard PDF",
            data=pdf_bytes,
            file_name="Wild_Data_Hub_Dashboard.pdf",
            mime="application/pdf",
        )

        st.caption(
            "Si le PDF ne s'affiche pas dans votre navigateur, "
            "utilisez le bouton de téléchargement."
        )

    else:
        st.error(
            "Le fichier dashboard.pdf est introuvable "
            "dans le dépôt GitHub."
        )


# ============================================================
# PAGE 3 — MACHINE LEARNING
# ============================================================

elif page == "Machine Learning":

    st.title("🤖 Machine Learning")
    st.subheader("Prédiction de l'espérance de vie")

    st.write(
        """
        Le projet intègre un modèle supervisé de régression
        linéaire permettant d'estimer l'espérance de vie
        à partir de quatre variables explicatives.
        """
    )

    st.markdown(
        """
        - **PIB par habitant**
        - **Taux de natalité**
        - **Accès à l'électricité**
        - **Émissions de CO₂ par habitant**
        """
    )

    st.write(
        """
        Les valeurs manquantes sont traitées par imputation
        à l'aide de la médiane.
        """
    )

    st.divider()

    st.header("Découpage chronologique")

    col1, col2 = st.columns(2)

    with col1:
        st.info("**Entraînement** : données jusqu'en 2019")

    with col2:
        st.info("**Évaluation** : données de 2020 à 2024")

    st.header("Performances du modèle")

    col1, col2, col3 = st.columns(3)

    col1.metric("MAE", "2,92 ans")
    col2.metric("RMSE", "3,84 ans")
    col3.metric("R²", "0,72")

    st.write(
        """
        Le modèle présente une erreur absolue moyenne
        de 2,92 ans sur le jeu de test.
        """
    )

    st.warning(
        "Les prédictions pour 2024 correspondent à une "
        "évaluation rétrospective du modèle et non "
        "à des prévisions futures."
    )

    st.write(
        """
        La cinquième page du dashboard Power BI présente
        les comparaisons entre les espérances de vie
        observées et estimées pour plusieurs pays.
        """
    )


# ============================================================
# PAGE 4 — PROJET & GITHUB
# ============================================================

elif page == "Projet & GitHub":

    st.title("💻 Projet & GitHub")

    st.subheader("Un pipeline Data Analyst automatisé")

    st.write(
        """
        Wild Data Hub couvre les principales étapes
        d'un projet de données :

        - Collecte depuis une API publique
        - Stockage des données dans BigQuery
        - Transformation et modélisation avec dbt
        - Contrôles de qualité des données
        - Entraînement et évaluation d'un modèle ML
        - Automatisation avec GitHub Actions
        - Visualisation avec Power BI
        """
    )

    st.divider()

    st.header("Documentation technique")

    st.write(
        """
        Le dépôt GitHub contient notamment :

        - Le README du projet
        - Les scripts Python
        - Les modèles et tests dbt
        - La documentation de la base de données
        - La documentation du dashboard Power BI
        - Le workflow GitHub Actions
        """
    )

    st.link_button(
        "🔗 Consulter le dépôt GitHub",
        GITHUB_URL,
    )

    st.divider()

    st.caption(
        "Wild Data Hub — Projet Data Analyst | Sébastien Nigaize"
    )


