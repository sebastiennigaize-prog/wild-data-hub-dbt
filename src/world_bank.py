import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

import requests

from src.config import (
    API_BASE_URL,
    INDICATORS,
    PER_PAGE,
    REQUEST_DELAY,
    REQUEST_TIMEOUT,
)


logger = logging.getLogger(__name__)


def calculer_hash(row: Any) -> str:
    """
    Calcule un hash SHA-256 à partir d'une ligne de données.

    Args:
        row: Donnée à transformer en chaîne JSON.

    Returns:
        Le hash SHA-256 de la donnée.
    """

    contenu = json.dumps(
        row,
        sort_keys=True,
        default=str,
    )

    return hashlib.sha256(
        contenu.encode("utf-8")
    ).hexdigest()


def recuperer_page_api(
    url: str,
    params: dict[str, Any],
) -> list[Any] | None:
    """
    Effectue une requête vers l'API World Bank.

    Args:
        url: URL de l'indicateur World Bank.
        params: Paramètres de la requête.

    Returns:
        La réponse JSON ou None en cas d'erreur.
    """

    try:
        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

    except requests.RequestException as e:
        logger.error(
            "Erreur lors de l'appel à l'API : %s",
            e,
        )
        return None

    if response.status_code != 200:
        logger.error(
            "Erreur HTTP lors de l'appel API : statut %s",
            response.status_code,
        )
        return None

    try:
        return response.json()

    except requests.exceptions.JSONDecodeError:
        logger.error(
            "La réponse de l'API n'est pas un JSON valide."
        )
        return None


def verifier_reponse_api(data: Any) -> bool:
    """
    Vérifie que la réponse API possède la structure attendue.

    Args:
        data: Réponse JSON retournée par l'API.

    Returns:
        True si la structure est valide, sinon False.
    """

    return (
        isinstance(data, list)
        and len(data) >= 2
        and isinstance(data[0], dict)
        and "total" in data[0]
        and "pages" in data[0]
        and data[1] is not None
    )


def construire_ligne_raw(
    code: str,
    nom_indicateur: str,
    ligne: dict[str, Any],
) -> dict[str, Any]:
    """
    Construit une ligne brute destinée à BigQuery.

    Args:
        code: Code de l'indicateur.
        nom_indicateur: Nom de l'indicateur.
        ligne: Observation brute de l'API.

    Returns:
        Une observation enrichie avec son hash
        et sa date d'insertion.
    """

    ligne_raw = {
        "indicator_code": code,
        "indicator_name": nom_indicateur,
        "data": ligne,
        "inserted_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    ligne_raw["row_hash"] = calculer_hash(
        ligne_raw["data"]
    )

    return ligne_raw


def recuperer_donnees_world_bank() -> list[dict[str, Any]]:
    """
    Récupère les indicateurs sélectionnés depuis l'API World Bank.

    Returns:
        Les observations brutes enrichies.

    Raises:
        ValueError: Si aucune donnée n'a été récupérée.
    """

    donnees: list[dict[str, Any]] = []

    for code, nom_indicateur in INDICATORS.items():

        url = (
            f"{API_BASE_URL}/"
            f"country/all/indicator/{code}"
        )

        params = {
            "format": "json",
            "per_page": PER_PAGE,
            "page": 1,
        }

        logger.info(
            "Récupération de l'indicateur %s (%s)",
            nom_indicateur,
            code,
        )

        lignes_recuperees = 0
        total = 0
        pages = 0

        while True:

            data = recuperer_page_api(
                url,
                params,
            )

            if data is None:
                logger.error(
                    "Récupération interrompue pour %s (%s)",
                    nom_indicateur,
                    code,
                )
                break

            if not verifier_reponse_api(data):
                logger.error(
                    "Structure de réponse inattendue "
                    "pour %s (%s)",
                    nom_indicateur,
                    code,
                )
                break

            metadata = data[0]
            lignes = data[1]

            total = metadata["total"]
            pages = metadata["pages"]

            page_actuelle = metadata.get(
                "page",
                params["page"],
            )

            logger.info(
                "%s (%s) : page %s/%s, %s lignes reçues",
                nom_indicateur,
                code,
                page_actuelle,
                pages,
                len(lignes),
            )

            for ligne in lignes:

                lignes_recuperees += 1

                donnees.append(
                    construire_ligne_raw(
                        code,
                        nom_indicateur,
                        ligne,
                    )
                )

            if page_actuelle >= pages:
                break

            params["page"] += 1
            time.sleep(REQUEST_DELAY)

        if lignes_recuperees != total:

            logger.warning(
                "%s (%s) : %s lignes récupérées "
                "sur %s annoncées",
                nom_indicateur,
                code,
                lignes_recuperees,
                total,
            )

        else:

            logger.info(
                "%s (%s) : vérification OK, "
                "%s lignes récupérées",
                nom_indicateur,
                code,
                lignes_recuperees,
            )

    if not donnees:
        logger.critical(
            "Aucune donnée récupérée depuis l'API World Bank."
        )

        raise ValueError(
            "Aucune donnée n'a été récupérée "
            "depuis l'API World Bank."
        )

    logger.info(
        "Récupération World Bank terminée : %s lignes",
        len(donnees),
    )

    return donnees
