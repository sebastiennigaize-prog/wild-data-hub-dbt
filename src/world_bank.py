import hashlib
import json
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
        print(f"❌ Erreur de requête : {e}")
        return None

    if response.status_code != 200:
        print(
            f"❌ Erreur HTTP : "
            f"{response.status_code}"
        )
        return None

    try:
        return response.json()

    except requests.exceptions.JSONDecodeError:
        print("❌ Réponse non-JSON")
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

        print(
            f"\n🔎 Récupération : "
            f"{nom_indicateur} ({code})"
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
                break

            if not verifier_reponse_api(data):
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
                params["page"],
            )

            print(
                f"   Page {page_actuelle}/{pages} "
                f"- {len(lignes)} lignes"
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