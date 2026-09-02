
import requests
import time
import hashlib
import json

from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from dotenv import load_dotenv
import os
from datetime import datetime, timezone


# ============================================================
# 1. CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
# ============================================================

load_dotenv()


# ============================================================
# 2. INDICATEURS WORLD BANK SÉLECTIONNÉS
# ============================================================

INDICATORS = {
    "NY.GDP.MKTP.CD": "PIB",
    "NY.GDP.PCAP.CD": "PIB_par_habitant",
    "NY.GDP.MKTP.KD.ZG": "Croissance_PIB",
    "SP.POP.TOTL": "Population",
    "SP.DYN.LE00.IN": "Esperance_vie",
    "SL.UEM.TOTL.ZS": "Chomage",
    "FP.CPI.TOTL.ZG": "Inflation",
    "EG.ELC.ACCS.ZS": "Acces_electricite",
    "EN.ATM.CO2E.PC": "CO2_par_habitant",
    "SP.DYN.CBRT.IN": "Taux_natalite",
    "SE.SEC.ENRR": "Scolarisation_secondaire",
    "SE.TER.ENRR": "Scolarisation_superieur",
    "SE.PRM.CMPT.ZS": "Achevement_primaire",
    "SH.XPD.CHEX.GD.ZS": "Depense_de_sante",
    "SE.XPD.TOTL.GD.ZS": "Depense_publique_education",
    "SE.ADT.LITR.ZS": "Alphabetisation_adultes",
}


# ============================================================
# 3. CONFIGURATION BIGQUERY
# ============================================================

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = "world_bank_raw"
TABLE_ID = "raw_data"

FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


# ============================================================
# 4. CALCUL DU HASH
# ============================================================

def calculer_hash(row):
    contenu = json.dumps(
        row,
        sort_keys=True,
        default=str
    )

    return hashlib.sha256(
        contenu.encode("utf-8")
    ).hexdigest()


# ============================================================
# 5. RÉCUPÉRATION DES DONNÉES WORLD BANK
# ============================================================

def recuperer_donnees_world_bank():

    donnees = []

    for code, nom_indicateur in INDICATORS.items():

        url = (
            f"https://api.worldbank.org/v2/"
            f"country/all/indicator/{code}"
        )

        params = {
            "format": "json",
            "per_page": 20000,
            "page": 1
        }

        print(
            f"\n🔎 Récupération : "
            f"{nom_indicateur} ({code})"
        )

        lignes_recuperees = 0
        total = 0
        pages = 0

        while True:

            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=30
                )

            except requests.RequestException as e:
                print(
                    f"❌ Erreur de requête : {e}"
                )
                break

            if response.status_code != 200:
                print(
                    f"❌ Erreur HTTP : "
                    f"{response.status_code}"
                )
                break

            try:
                data = response.json()

            except requests.exceptions.JSONDecodeError:
                print("❌ Réponse non-JSON")
                break

            # ------------------------------------------------
            # Vérification de la structure
            # ------------------------------------------------

            if (
                not isinstance(data, list)
                or len(data) < 2
                or not isinstance(data[0], dict)
                or "total" not in data[0]
                or "pages" not in data[0]
                or data[1] is None
            ):
                print(
                    "❌ Structure de réponse inattendue"
                )
                break

            metadata = data[0]
            lignes = data[1]

            total = metadata["total"]
            pages = metadata["pages"]

            page_actuelle = metadata.get(
                "page",
                params["page"]
            )

            print(
                f"   Page {page_actuelle}/{pages} "
                f"- {len(lignes)} lignes"
            )

            # ------------------------------------------------
            # Conservation du JSON brut
            # ------------------------------------------------

            for ligne in lignes:

                lignes_recuperees += 1

                ligne_raw = {
                    "indicator_code": code,
                    "indicator_name": nom_indicateur,
                    "data": ligne,
                    "inserted_at": datetime.now(
                        timezone.utc
                    ).isoformat()
                }

                ligne_raw["row_hash"] = (
                    calculer_hash(ligne_raw["data"])
                )

                donnees.append(ligne_raw)

            # ------------------------------------------------
            # Pagination
            # ------------------------------------------------

            if page_actuelle >= pages:
                break

            params["page"] += 1

            time.sleep(0.5)

        # ----------------------------------------------------
        # Vérification du nombre de lignes
        # ----------------------------------------------------

        if lignes_recuperees != total:

            print(
                f"⚠️ Attention : "
                f"{lignes_recuperees} lignes récupérées "
                f"sur {total} annoncées par l'API."
            )

        else:

            print(
                f"✅ Vérification OK : "
                f"{lignes_recuperees} lignes récupérées "
                f"sur {total} annoncées."
            )

    if not donnees:
        raise ValueError(
            "Aucune donnée n'a été récupérée "
            "depuis l'API World Bank."
        )

    print(
        f"\n📊 Total de lignes récupérées : "
        f"{len(donnees)}"
    )

    return donnees

# ============================================================
# 6. RÉCUPÉRATION DES HASH EXISTANTS
# ============================================================

def recuperer_hash_existants(client):

    try:

        client.get_table(FULL_TABLE_ID)

        query = f"""
            SELECT row_hash
            FROM `{FULL_TABLE_ID}`
            ORDER BY inserted_at DESC
            LIMIT 50000
        """

        result = client.query(query).result()

        existing_hashes = {
            row.row_hash
            for row in result
        }

        print(
            f"🔎 Hash récupérés : "
            f"{len(existing_hashes)}"
        )

        return existing_hashes

    except NotFound:

        print(
            "ℹ️ La table BigQuery n'existe pas encore."
        )

        return set()


# ============================================================
# 7. INGESTION DANS BIGQUERY
# ============================================================

def ingest_data():

    print(
        "\n=== INGESTION WORLD BANK → BIGQUERY ==="
    )

    donnees = recuperer_donnees_world_bank()

    client = bigquery.Client()

    existing_hashes = recuperer_hash_existants(
        client
    )

    nouvelles_donnees = [
        ligne
        for ligne in donnees
        if ligne["row_hash"]
        not in existing_hashes
    ]

    print(
        f"🆕 Nouvelles lignes : "
        f"{len(nouvelles_donnees)}"
    )

    if not nouvelles_donnees:

        print(
            "✅ Aucune nouvelle donnée "
            "à insérer."
        )

        return

    # --------------------------------------------------------
    # Chargement JSON direct dans BigQuery
    # --------------------------------------------------------

    job_config = bigquery.LoadJobConfig(
        write_disposition=
        bigquery.WriteDisposition.WRITE_APPEND,
        autodetect=True
    )

    load_job = client.load_table_from_json(
        nouvelles_donnees,
        FULL_TABLE_ID,
        job_config=job_config
    )

    load_job.result()

    print(
        f"✅ {len(nouvelles_donnees)} "
        f"nouvelles lignes insérées dans "
        f"{FULL_TABLE_ID}"
    )


# ============================================================
# 8. LANCEMENT DU SCRIPT
# ============================================================

if __name__ == "__main__":

    ingest_data()
