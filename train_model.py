import joblib
import numpy as np
import pandas as pd

from google.cloud import bigquery
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline


# ============================================================
# 1. CONFIGURATION
# ============================================================

PROJECT_ID = "data-quest-sebastien"
TABLE_FEATURES = f"{PROJECT_ID}.marts.world_bank_features"

COLONNE_CIBLE = "esperance_vie"

COLONNES_EXPLICATIVES = [
    "pib_par_habitant",
    "taux_natalite",
    "acces_electricite",
    "co2_par_habitant",
]

DERNIERE_ANNEE_ENTRAINEMENT = 2019
PREMIERE_ANNEE_TEST = 2020
DERNIERE_ANNEE_TEST = 2024


# ============================================================
# 2. CHARGEMENT DES DONNEES DEPUIS BIGQUERY
# ============================================================

def charger_donnees():
    client = bigquery.Client(project=PROJECT_ID)

    requete = f"""
        SELECT
            countryiso3code,
            annee,
            esperance_vie,
            pib_par_habitant,
            taux_natalite,
            acces_electricite,
            co2_par_habitant
        FROM `{TABLE_FEATURES}`
    """

    df = client.query(requete).to_dataframe(
        create_bqstorage_client=False
    )

    print(f"Nombre total de lignes : {len(df)}")

    return df


# ============================================================
# 3. PREPARATION DES DONNEES
# ============================================================

def preparer_donnees(df):
    # Les lignes sans esperance de vie connue ne peuvent pas
    # servir a entrainer ou evaluer le modele.
    df = df.dropna(subset=[COLONNE_CIBLE]).copy()

    # Conversion des colonnes numeriques.
    colonnes_numeriques = [
        "annee",
        COLONNE_CIBLE,
        *COLONNES_EXPLICATIVES,
    ]

    for colonne in colonnes_numeriques:
        df[colonne] = pd.to_numeric(
            df[colonne],
            errors="coerce"
        ).astype("float64")

    df = df.dropna(subset=["annee", COLONNE_CIBLE])

    print(
        "Lignes avec esperance de vie connue : "
        f"{len(df)}"
    )

    return df


# ============================================================
# 4. CREATION DU PIPELINE ML
# ============================================================

def creer_pipeline():
    # La mediane sera calculee uniquement sur les donnees
    # d'entrainement. Les vrais zeros sont conserves.
    preparation = ColumnTransformer(
        transformers=[
            (
                "numerique",
                SimpleImputer(
                    strategy="median",
                    keep_empty_features=True
                ),
                COLONNES_EXPLICATIVES,
            )
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("preparation", preparation),
            ("modele", LinearRegression()),
        ]
    )

    return pipeline


# ============================================================
# 5. ENTRAINEMENT ET EVALUATION CHRONOLOGIQUE
# ============================================================

def entrainer_modele():
    df = charger_donnees()
    df = preparer_donnees(df)

    # Entrainement : annees jusqu'en 2019 inclus.
    df_train = df[
        df["annee"] <= DERNIERE_ANNEE_ENTRAINEMENT
    ].copy()

    # Test : annees 2020 a 2024 inclus.
    df_test = df[
        (df["annee"] >= PREMIERE_ANNEE_TEST)
        & (df["annee"] <= DERNIERE_ANNEE_TEST)
    ].copy()

    if df_train.empty or df_test.empty:
        raise ValueError(
            "La periode d'entrainement ou de test est vide."
        )

    X_train = df_train[COLONNES_EXPLICATIVES]
    y_train = df_train[COLONNE_CIBLE]

    X_test = df_test[COLONNES_EXPLICATIVES]
    y_test = df_test[COLONNE_CIBLE]

    print("\n===== SEPARATION CHRONOLOGIQUE =====")
    print(
        "Entrainement : "
        f"{int(df_train['annee'].min())} a "
        f"{int(df_train['annee'].max())}"
    )
    print(f"Lignes d'entrainement : {len(df_train)}")

    print(
        "Test : "
        f"{int(df_test['annee'].min())} a "
        f"{int(df_test['annee'].max())}"
    )
    print(f"Lignes de test : {len(df_test)}")

    print(
        "\nValeurs manquantes dans les variables "
        "explicatives du test :"
    )
    print(X_test.isna().sum())

    pipeline = creer_pipeline()
    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(
        mean_squared_error(y_test, predictions)
    )
    r2 = r2_score(y_test, predictions)

    print("\n===== RESULTATS DU MODELE =====")
    print(f"MAE  : {mae:.2f} ans")
    print(f"RMSE : {rmse:.2f} ans")
    print(f"R2   : {r2:.4f}")

    # On conserve le premier pipeline.pkl pour pouvoir
    # comparer les resultats avant de le remplacer.
    nom_fichier = "pipeline_chronologique.pkl"

    joblib.dump(pipeline, nom_fichier)

    print(f"\nModele sauvegarde dans {nom_fichier}")


# ============================================================
# 6. EXECUTION
# ============================================================

if __name__ == "__main__":
    entrainer_modele()