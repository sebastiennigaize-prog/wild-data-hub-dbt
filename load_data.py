from google.cloud import bigquery

from src.bigquery_io import (
    charger_donnees_bigquery,
    filtrer_nouvelles_donnees,
    recuperer_hash_existants,
)
from src.config import FULL_TABLE_ID
from src.world_bank import recuperer_donnees_world_bank


def ingest_data() -> None:
    """
    Orchestre l'ingestion des données World Bank vers BigQuery.
    """

    print(
        "\n=== INGESTION WORLD BANK → BIGQUERY ==="
    )

    donnees = recuperer_donnees_world_bank()

    client = bigquery.Client()

    existing_hashes = recuperer_hash_existants(
        client
    )

    nouvelles_donnees = filtrer_nouvelles_donnees(
        donnees,
        existing_hashes,
    )

    print(
        f"🆕 Nouvelles lignes : "
        f"{len(nouvelles_donnees)}"
    )

    if not nouvelles_donnees:
        print(
            "✅ Aucune nouvelle donnée à insérer."
        )
        return

    charger_donnees_bigquery(
        client,
        nouvelles_donnees,
    )

    print(
        f"✅ {len(nouvelles_donnees)} "
        f"nouvelles lignes insérées dans "
        f"{FULL_TABLE_ID}"
    )


def main() -> None:
    """
    Lance le pipeline d'ingestion Wild Data Hub.
    """

    ingest_data()


if __name__ == "__main__":
    main()