# Wild Data Hub — Analyse des indicateurs de la Banque mondiale

## Présentation du projet

Ce projet Data Analyst exploite des données issues de l'API de la Banque mondiale afin d'analyser l'évolution d'indicateurs économiques, démographiques, sociaux et environnementaux à l'échelle internationale.

Les données sont collectées depuis l'API World Bank, stockées dans Google BigQuery puis transformées avec dbt afin de construire des tables adaptées à l'analyse et à la visualisation.

Le projet intègre également un modèle de Machine Learning permettant d'estimer l'espérance de vie à partir de quatre variables explicatives :

- PIB par habitant ;
- taux de natalité ;
- accès à l'électricité ;
- émissions de CO₂ par habitant.

Les résultats et les prédictions sont exploités dans un tableau de bord Power BI interactif.

## Architecture du pipeline

Le projet suit une chaîne de traitement automatisée allant de la collecte des données jusqu'à leur exploitation analytique.

```text
API World Bank
      ↓
Python — load_data.py
      ↓
Google BigQuery — données brutes
      ↓
dbt
      ├── staging
      ├── dimensions
      ├── table de faits
      └── marts analytiques
      ↓
world_bank_features
      ↓
Machine Learning — scikit-learn
      ↓
Prédictions enregistrées dans BigQuery
      ↓
Power BI
```

Le pipeline est orchestré par `run_pipeline.py`. Il exécute successivement l'ingestion des données, les transformations et tests dbt, puis la génération des prédictions du modèle de Machine Learning.

Son exécution est automatisée avec GitHub Actions.

## Technologies utilisées

- **Python** : collecte des données, préparation et Machine Learning
- **Google BigQuery** : stockage des données et des prédictions
- **dbt** : transformation, modélisation et tests de qualité des données
- **scikit-learn** : entraînement et utilisation du modèle de Machine Learning
- **GitHub Actions** : automatisation de l'exécution du pipeline
- **Power BI** : analyse et visualisation des données
- **Git / GitHub** : versionnement et gestion du projet

## Modélisation des données avec dbt

Les données brutes provenant de la Banque mondiale sont transformées avec dbt afin de construire un modèle adapté à l'analyse.

### Staging

- `stg_world_bank` : prépare et standardise les données issues de la table source BigQuery.

### Modèle dimensionnel

- `dim_pays` : dimension contenant les pays et leur code ISO3.
- `dim_annee` : dimension temporelle contenant les années.
- `dim_indicator` : dimension contenant les codes et libellés des indicateurs.
- `fact_indicators` : table de faits contenant une observation par pays, année et indicateur.

### Tables analytiques

- `mart_country_indicators` : transforme les indicateurs au format large afin d'obtenir une ligne par pays et par année.
- `world_bank_features` : sélectionne les variables nécessaires au modèle de Machine Learning.

## Qualité des données

La qualité des données est contrôlée avec des tests dbt intégrés au pipeline.

Les tests permettent notamment de vérifier :

- l'absence de valeurs nulles sur les clés principales ;
- l'unicité des clés des dimensions ;
- la cohérence des relations entre la table de faits et les dimensions ;
- la validité des données transformées avant leur utilisation par le modèle de Machine Learning.

La commande `dbt build` exécute les modèles et leurs tests avant de lancer les prédictions.

Lors de la dernière exécution du pipeline, les 17 tests dbt ont été exécutés avec succès.

## Machine Learning — Prédiction de l'espérance de vie

Le projet intègre un modèle supervisé de régression linéaire dont l'objectif est d'estimer l'espérance de vie d'un pays.

### Variables utilisées

La variable cible est :

- `esperance_vie`

Les variables explicatives sont :

- `pib_par_habitant`
- `taux_natalite`
- `acces_electricite`
- `co2_par_habitant`

Les valeurs manquantes sont traitées dans le pipeline scikit-learn par une imputation utilisant la médiane.

### Découpage chronologique

Afin de respecter l'ordre temporel des données, l'entraînement et l'évaluation sont séparés chronologiquement :

- entraînement : données jusqu'en 2019 ;
- test : données de 2020 à 2024.

### Performances du modèle

Les performances obtenues sur le jeu de test sont :

- MAE : 2,92 ans
- RMSE : 3,84 ans
- R² : 0,7209

Le modèle entraîné est enregistré dans le fichier `pipeline_chronologique.pkl`.

Le script `predict.py` charge ce modèle, récupère les données préparées par dbt dans BigQuery, génère les prédictions puis les enregistre dans la table `ml.predictions`.

## Automatisation du pipeline

L'exécution du pipeline est automatisée avec GitHub Actions grâce au workflow `.github/workflows/pipeline.yml`.

Le workflow peut être lancé manuellement depuis GitHub Actions et prévoit également une exécution planifiée.

À chaque exécution, les étapes suivantes sont réalisées :

1. récupération du dépôt GitHub ;
2. installation de Python et des dépendances ;
3. configuration de l'authentification Google Cloud ;
4. ingestion des données de l'API World Bank vers BigQuery ;
5. exécution de `dbt build` pour construire et tester les modèles ;
6. génération des prédictions avec le modèle de Machine Learning ;
7. enregistrement des prédictions dans BigQuery.

Le pipeline utilise une clé de compte de service Google Cloud stockée dans les secrets GitHub afin de ne pas exposer les informations d'authentification dans le dépôt.

## Installation et exécution

### Prérequis

Pour exécuter le projet, les éléments suivants sont nécessaires :

- Python 3.12 ;
- un projet Google Cloud avec BigQuery activé ;
- un compte de service disposant des droits nécessaires sur BigQuery ;
- dbt avec l'adaptateur BigQuery.

### Installation des dépendances

Les dépendances Python sont définies dans le fichier `requirements.txt`.

```bash
pip install -r requirements.txt
```

### Configuration

Les informations de connexion à Google Cloud doivent être configurées avant l'exécution du pipeline.

Le projet utilise notamment les variables d'environnement nécessaires à l'authentification Google Cloud et à l'identification du projet GCP.

Les informations sensibles, notamment la clé du compte de service, ne doivent pas être enregistrées directement dans le dépôt GitHub.

### Exécution du pipeline

Le pipeline complet peut être lancé avec :

```bash
python run_pipeline.py
```

Cette commande exécute successivement :

1. l'ingestion des données World Bank ;
2. les transformations et tests dbt ;
3. la génération des prédictions Machine Learning ;
4. l'enregistrement des prédictions dans BigQuery.

Le pipeline peut également être exécuté depuis GitHub Actions.

## Restitution avec Power BI

Les données préparées dans BigQuery sont exploitées dans Power BI afin de construire un tableau de bord interactif consacré aux indicateurs de développement internationaux.

Le tableau de bord permet notamment d'analyser :

- les indicateurs économiques et démographiques ;
- l'emploi et l'inflation ;
- les indicateurs environnementaux et éducatifs ;
- l'évolution des indicateurs dans le temps et selon les pays.

Une page spécifique est consacrée au modèle de Machine Learning. Elle compare, pour l'année 2024, l'espérance de vie observée avec l'espérance de vie estimée par le modèle et présente l'erreur absolue de prédiction.

Les résultats affichés pour 2024 appartiennent à la période de test du modèle (2020–2024) et ne constituent donc pas des prévisions futures.