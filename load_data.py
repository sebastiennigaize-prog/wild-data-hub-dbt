import logging
from datetime import datetime, timezone

from google.cloud import bigquery

from src.bigquery_io import (
    annuler_le_lot,
    charger_donnees_bigquery,
    filtrer_nouvelles_donnees,
    recuperer_hash_existants,
)
from src.config import FULL_TABLE_ID
from src.world_bank import recuperer_donnees_world_bank


# ============================================================
# 1. CONFIGURATION DU LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - %(name)s - "
        "%(levelname)s - %(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# ============================================================
# 2. INGESTION
# ============================================================

def ingest_data() -> None:
    """
    Orchestre l'ingestion des données World Bank vers BigQuery.

    Un batch_id unique est créé pour chaque exécution.
    En cas d'erreur pendant l'ingestion, les lignes du lot
    sont supprimées afin de restaurer l'état précédent.
    """

    batch_id = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S")

    logger.info(
        "Début de l'ingestion, batch_id=%s",
        batch_id,
    )

    client = bigquery.Client()

    try:
        donnees = recuperer_donnees_world_bank()

        logger.info(
            "Données récupérées depuis l'API : %s lignes",
            len(donnees),
        )

        existing_hashes = recuperer_hash_existants(
            client
        )

        nouvelles_donnees = filtrer_nouvelles_donnees(
            donnees,
            existing_hashes,
        )

        if not nouvelles_donnees:
            logger.info(
                "Aucune nouvelle donnée à insérer, "
                "batch_id=%s",
                batch_id,
            )
            return

        charger_donnees_bigquery(
            client,
            nouvelles_donnees,
            batch_id,
        )

        logger.info(
            "Ingestion terminée : %s lignes insérées "
            "dans %s, batch_id=%s",
            len(nouvelles_donnees),
            FULL_TABLE_ID,
            batch_id,
        )

    except Exception:
        logger.exception(
            "Ingestion interrompue, "
            "début du rollback, batch_id=%s",
            batch_id,
        )

        try:
            annuler_le_lot(
                client,
                batch_id,
            )

            logger.warning(
                "Rollback terminé, batch_id=%s",
                batch_id,
            )

        except Exception:
            logger.exception(
                "Échec du rollback, batch_id=%s",
                batch_id,
            )

        raise


# ============================================================
# 3. POINT D'ENTRÉE
# ============================================================

def main() -> None:
    """
    Lance le pipeline d'ingestion Wild Data Hub.
    """

    ingest_data()


if __name__ == "__main__":
    main()