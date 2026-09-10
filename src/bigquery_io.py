import logging
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.config import FULL_TABLE_ID, HASH_LIMIT


logger = logging.getLogger(__name__)


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

        logger.info(
            "Hash récupérés : %s",
            len(existing_hashes),
        )

        return existing_hashes

    except NotFound:
        logger.info(
            "La table BigQuery n'existe pas encore."
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

    nouvelles_donnees = [
        ligne
        for ligne in donnees
        if ligne["row_hash"] not in existing_hashes
    ]

    logger.info(
        "Nouvelles lignes détectées : %s",
        len(nouvelles_donnees),
    )

    return nouvelles_donnees


def ajouter_batch_id(
    donnees: list[dict[str, Any]],
    batch_id: str,
) -> list[dict[str, Any]]:
    """
    Ajoute l'identifiant du lot aux lignes à insérer.

    Args:
        donnees: Données à enrichir.
        batch_id: Identifiant unique de l'exécution.

    Returns:
        Les données enrichies avec le batch_id.
    """

    donnees_enrichies = []

    for ligne in donnees:
        ligne_enrichie = dict(ligne)
        ligne_enrichie["batch_id"] = batch_id
        donnees_enrichies.append(ligne_enrichie)

    return donnees_enrichies


def charger_donnees_bigquery(
    client: bigquery.Client,
    donnees: list[dict[str, Any]],
    batch_id: str,
) -> None:
    """
    Charge directement les données JSON dans BigQuery.

    Args:
        client: Client BigQuery.
        donnees: Données à charger.
        batch_id: Identifiant unique du lot.
    """

    donnees_enrichies = ajouter_batch_id(
        donnees,
        batch_id,
    )

    job_config = bigquery.LoadJobConfig(
        write_disposition=(
            bigquery.WriteDisposition.WRITE_APPEND
        ),
        autodetect=True,
        schema_update_options=[
            bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
        ],
    )

    load_job = client.load_table_from_json(
        donnees_enrichies,
        FULL_TABLE_ID,
        job_config=job_config,
    )

    load_job.result()

    logger.info(
        "Insertion terminée : %s lignes ajoutées, batch_id=%s",
        len(donnees_enrichies),
        batch_id,
    )


def annuler_le_lot(
    client: bigquery.Client,
    batch_id: str,
) -> None:
    """
    Supprime toutes les lignes appartenant à un lot.

    Cette fonction joue le rôle de rollback pour
    l'ingestion Python.

    Args:
        client: Client BigQuery.
        batch_id: Identifiant du lot à supprimer.
    """

    requete = f"""
        DELETE FROM `{FULL_TABLE_ID}`
        WHERE batch_id = @batch_id
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "batch_id",
                "STRING",
                batch_id,
            )
        ]
    )

    client.query(
        requete,
        job_config=job_config,
    ).result()

    logger.warning(
        "Rollback effectué : lot %s supprimé",
        batch_id,
    )