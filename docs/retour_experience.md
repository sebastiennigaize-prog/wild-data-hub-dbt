# Wild Data Hub — Retour d'expérience technique

**Projet Data Analyst :** analyse des indicateurs de développement de la Banque mondiale  
**[Application Streamlit](https://wild-data-sebastien.streamlit.app/)** · **[Dépôt GitHub](https://github.com/sebastiennigaize-prog/wild-data-hub-dbt)**

Ce document présente les principaux incidents résolus et choix techniques réalisés pendant la conception d'un pipeline de données allant de l'API Banque mondiale à BigQuery, dbt, un modèle de Machine Learning et Power BI.

> Les incidents constatés sont distingués des choix de conception. Les chiffres et extraits de code correspondent aux éléments documentés pendant le projet.

## 1. Corriger une déduplication incomplète dans BigQuery

**Incident.** Un problème d'ingestion a conduit à **2 071 547 doublons**. Le contrôle des données existantes reposait sur les 50 000 empreintes (`row_hash`) les plus récentes :

```sql
SELECT row_hash
FROM `table`
ORDER BY inserted_at DESC
LIMIT 50000
```

**Diagnostic.** Une empreinte plus ancienne pouvait ne pas figurer parmi les 50 000 dernières lignes. Un enregistrement déjà présent pouvait alors être traité comme nouveau.

**Correction.** Le contrôle a été étendu à toutes les empreintes non nulles :

```sql
SELECT DISTINCT row_hash
FROM `table`
WHERE row_hash IS NOT NULL
```

Les doublons déjà présents ont également été supprimés lors d'une opération de nettoyage distincte. `DISTINCT` ne supprime pas, à lui seul, les doublons de la table source.

**Enseignement.** Une limitation de volume peut accélérer une requête tout en rendant un contrôle de qualité incomplet. La déduplication doit couvrir le périmètre pertinent, y compris lors des réexécutions.

## 2. Résoudre une incompatibilité de dépendances dans GitHub Actions

**Incident.** L'installation des dépendances du pipeline échouait dans GitHub Actions. Les logs ont mis en évidence une incompatibilité entre Python 3.11 et la version de NumPy demandée (`numpy==2.5.2`).

**Correction.** Le workflow final utilise Python 3.12 :

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
```

L'historique des exécutions partagé montre ensuite plusieurs déclenchements automatiques réussis. Ces résultats confirment le fonctionnement du workflow final, sans prouver que ce seul changement explique chaque réussite.

**Enseignement.** Les versions de Python et des bibliothèques doivent être compatibles et cohérentes entre développement local et environnement automatisé.

## 3. Faire respecter l'unicité d'une dimension avec dbt

**Incident.** Le 4 octobre 2026, le test `unique_dim_indicator_indicator_key` a échoué. Un même code d'indicateur pouvait être associé à plusieurs libellés, alors que la dimension devait comporter une ligne par code.

**Correction.** Le modèle final agrège les lignes par `indicator_code` :

```sql
SELECT
    indicator_code AS indicator_key,
    indicator_code,
    MAX(indicator_name) AS indicator_name
FROM {{ ref('stg_world_bank') }}
WHERE indicator_code IS NOT NULL
GROUP BY indicator_code
```

Les exécutions ultérieures ont réussi. Le pipeline comprend **26 opérations dbt : 6 modèles table, 1 modèle vue et 19 tests**.

**Limite connue.** `MAX(indicator_name)` sélectionne un libellé selon l'ordre SQL ; ce n'est pas nécessairement le nom métier le plus pertinent. Une table de correspondance de référence serait une amélioration possible.

**Enseignement.** Un test d'unicité bloquant permet de détecter une anomalie de modélisation avant l'exploitation des données.

## 4. Préparer les données de Machine Learning sans fuite temporelle

**Choix méthodologique, et non incident constaté.** Le modèle de régression linéaire estime l'espérance de vie à partir du PIB par habitant, du taux de natalité, de l'accès à l'électricité et des émissions de CO₂ par habitant.

Dans `train_model.py` :

- Les observations sans valeur cible connue sont écartées.
- Les valeurs manquantes des variables explicatives sont imputées par la médiane dans un `Pipeline` scikit-learn, ajusté sur le jeu d'entraînement uniquement.
- Les années **jusqu'en 2019** servent à l'entraînement ; **2020–2024** sert à l'évaluation.

**Résultats observés :** MAE **2,92 ans**, RMSE **3,84 ans**, R² **environ 0,72**.

**Enseignement.** La préparation doit être intégrée au processus d'entraînement et l'évaluation doit respecter la chronologie. Ce découpage ne supprime pas automatiquement tous les risques de fuite de données.

## 5. Rendre les résultats du modèle exploitables dans Power BI

**Défi d'intégration, et non incident constaté.** Le script `predict.py` recharge le pipeline sauvegardé avec `joblib`, récupère les observations de **2024** depuis BigQuery, calcule `esperance_vie_predite` et l'erreur absolue lorsqu'une valeur observée existe, puis charge les résultats dans `ml.predictions`.

Le chargement utilise `WRITE_TRUNCATE` afin de remplacer les résultats précédents lors d'une exécution réussie, sans les empiler.

**Précision métier :** les estimations pour 2024 sont **rétrospectives**, car cette année appartient à la période de test ; ce ne sont pas des prévisions d'années futures.

## 6. Corriger l'affichage du rapport Power BI dans Streamlit

**Incident.** Après déploiement, le rapport PDF s'affichait sous forme d'une zone grise dans un lecteur intégré, alors que son téléchargement fonctionnait.

**Diagnostic.** Le PDF était accessible ; le problème concernait son rendu dans l'interface.

**Correction.** L'intégration par iframe a été remplacée par un rendu page par page avec **PyMuPDF**, puis `st.image()` ; le téléchargement du PDF original a été conservé.

**Résultat.** Les **six pages** du rapport sont consultables dans [l'application Streamlit](https://wild-data-sebastien.streamlit.app/). La présentation reste non interactive : elle ne reproduit pas les filtres de Power BI Desktop.

## Bilan et pistes d'amélioration

Ces situations illustrent une démarche de diagnostic fondée sur les logs, les contrôles SQL, les tests dbt et la vérification des résultats après correction.

Pistes envisagées, **non présentées comme déjà réalisées** : stratégie de déduplication incrémentale côté BigQuery ; table de référence pour les libellés d'indicateurs ; alertes sur les échecs ; analyse des erreurs ML par pays ou région ; publication éventuelle d'un rapport interactif.
