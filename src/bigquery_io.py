from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.config import FULL_TABLE_ID, HASH_LIMIT


def recuperer_hash_existants(
    client: bigquery.Client,
) -> set[str]:
    """
    Récupère les hash récents présents dans BigQuery.

    Args:
        client: Client BigQuery.

    Returns:
        Un ensemble contenant les hash existants.
    """

    try:
        client.get_table(FULL_TABLE_ID)

        query = f"""
            SELECT row_hash
            FROM `{FULL_TABLE_ID}`
            ORDER BY inserted_at DESC
            LIMIT {HASH_LIMIT}
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


def filtrer_nouvelles_donnees(
    donnees: list[dict[str, Any]],
    existing_hashes: set[str],
) -> list[dict[str, Any]]:
    """
    Conserve uniquement les données absentes de BigQuery.

    Args:
        donnees: Données récupérées depuis l'API.
        existing_hashes: Hash présents dans BigQuery.

    Returns:
        Les nouvelles données à insérer.
    """

    return [
        ligne
        for ligne in donnees
        if ligne["row_hash"] not in existing_hashes
    ]


def charger_donnees_bigquery(
    client: bigquery.Client,
    donnees: list[dict[str, Any]],
) -> None:
    """
    Charge directement les données JSON dans BigQuery.

    Args:
        client: Client BigQuery.
        donnees: Données à charger.
    """

    job_config = bigquery.LoadJobConfig(
        write_disposition=(
            bigquery.WriteDisposition.WRITE_APPEND
        ),
        autodetect=True,
    )

    load_job = client.load_table_from_json(
        donnees,
        FULL_TABLE_ID,
        job_config=job_config,
    )

    load_job.result()