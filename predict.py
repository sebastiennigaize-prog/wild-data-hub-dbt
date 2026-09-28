import joblib
import pandas as pd

from google.cloud import bigquery


# ============================================================
# 1. CONFIGURATION
# ============================================================

PROJECT_ID = "data-quest-sebastien"

TABLE_FEATURES = f"{PROJECT_ID}.marts.world_bank_features"
TABLE_PREDICTIONS = f"{PROJECT_ID}.ml.predictions"

FICHIER_MODELE = "pipeline_chronologique.pkl"

ANNEE_PREDICTION = 2024

COLONNES_EXPLICATIVES = [
    "pib_par_habitant",
    "taux_natalite",
    "acces_electricite",
    "co2_par_habitant",
]


# ============================================================
# 2. CHARGEMENT DES DONNEES
# ============================================================

def charger_donnees(client):
    requete = f"""
        SELECT
            country_name,
            countryiso3code,
            annee,
            esperance_vie,
            pib_par_habitant,
            taux_natalite,
            acces_electricite,
            co2_par_habitant
        FROM `{TABLE_FEATURES}`
        WHERE annee = @annee
          AND countryiso3code IS NOT NULL
          AND TRIM(countryiso3code) != ''
    """

    configuration = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "annee",
                "INT64",
                ANNEE_PREDICTION,
            )
        ]
    )

    df = client.query(
        requete,
        job_config=configuration,
    ).to_dataframe(create_bqstorage_client=False)

    print(f"Lignes recuperees pour {ANNEE_PREDICTION} : {len(df)}")

    return df


# ============================================================
# 3. PREDICTIONS
# ============================================================

def calculer_predictions(df):
    pipeline = joblib.load(FICHIER_MODELE)

    X = df[COLONNES_EXPLICATIVES].copy()

    for colonne in COLONNES_EXPLICATIVES:
        X[colonne] = pd.to_numeric(
            X[colonne],
            errors="coerce",
        ).astype("float64")

    df_resultats = df[
        [
            "country_name",
            "countryiso3code",
            "annee",
            "esperance_vie",
        ]
    ].copy()

    df_resultats["esperance_vie_predite"] = pipeline.predict(X)

    df_resultats["erreur_absolue"] = (
        df_resultats["esperance_vie"]
        - df_resultats["esperance_vie_predite"]
    ).abs()

    print("\nApercu des predictions :")
    print(df_resultats.head(10).to_string(index=False))

    return df_resultats


# ============================================================
# 4. ENREGISTREMENT DANS BIGQUERY
# ============================================================

def enregistrer_predictions(client, df_resultats):
    # Creation du dataset ML s'il n'existe pas.
    dataset = bigquery.Dataset(f"{PROJECT_ID}.ml")
    client.create_dataset(dataset, exists_ok=True)

    configuration = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema=[
            bigquery.SchemaField("country_name", "STRING"),
            bigquery.SchemaField("countryiso3code", "STRING"),
            bigquery.SchemaField("annee", "INTEGER"),
            bigquery.SchemaField("esperance_vie", "FLOAT"),
            bigquery.SchemaField("esperance_vie_predite", "FLOAT"),
            bigquery.SchemaField("erreur_absolue", "FLOAT"),
        ],
    )

    job = client.load_table_from_dataframe(
        df_resultats,
        TABLE_PREDICTIONS,
        job_config=configuration,
    )

    job.result()

    print(
        f"\n{len(df_resultats)} predictions enregistrees "
        f"dans {TABLE_PREDICTIONS}"
    )


# ============================================================
# 5. EXECUTION
# ============================================================

def main():
    client = bigquery.Client(project=PROJECT_ID)

    df = charger_donnees(client)

    if df.empty:
        raise ValueError(
            f"Aucune donnee disponible pour {ANNEE_PREDICTION}."
        )

    df_resultats = calculer_predictions(df)

    enregistrer_predictions(client, df_resultats)


if __name__ == "__main__":
    main()