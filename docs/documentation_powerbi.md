# Documentation du tableau de bord Power BI

## Présentation

Le tableau de bord Power BI du projet Wild Data Hub permet d'explorer des indicateurs de développement issus de la Banque mondiale.

Il est destiné à faciliter l'analyse comparative des pays et l'étude de l'évolution des indicateurs économiques, démographiques, sociaux, éducatifs et environnementaux.

Une partie du tableau de bord est également consacrée aux résultats du modèle de Machine Learning développé pour estimer l'espérance de vie.

## Sources des données

Les données proviennent de l'API publique de la Banque mondiale.

Elles sont :

1. collectées avec Python ;
2. stockées dans Google BigQuery ;
3. transformées et contrôlées avec dbt ;
4. utilisées dans Power BI pour la visualisation.

Les prédictions du modèle de Machine Learning sont également enregistrées dans BigQuery avant leur exploitation dans Power BI.

## Mise à jour des données

Le pipeline de données peut être exécuté automatiquement avec GitHub Actions.

À chaque exécution, il réalise l'ingestion des données, les transformations et tests dbt, puis la génération des prédictions Machine Learning.

La mise à jour des données dans BigQuery ne signifie pas nécessairement que les données affichées dans Power BI sont immédiatement actualisées : l'actualisation du tableau de bord dépend également du mode de connexion et de l'actualisation configurée dans Power BI.

## Utilisation du tableau de bord

Le tableau de bord permet notamment :

- de sélectionner une année ;
- de sélectionner un pays ;
- de comparer plusieurs indicateurs ;
- d'observer leur évolution dans le temps ;
- de comparer différents pays ;
- d'analyser les résultats du modèle de Machine Learning.

Les filtres présents sur les pages permettent d'adapter les graphiques au pays ou à la période étudiée.

## Principaux indicateurs

| Indicateur | Définition |
|---|---|
| PIB | Produit intérieur brut du pays. |
| PIB par habitant | Produit intérieur brut rapporté à la population. |
| Croissance du PIB | Évolution annuelle du PIB en pourcentage. |
| Population | Population totale. |
| Espérance de vie | Espérance de vie à la naissance, exprimée en années. |
| Chômage | Taux de chômage. |
| Inflation | Évolution générale du niveau des prix. |
| Accès à l'électricité | Part de la population ayant accès à l'électricité. |
| CO₂ par habitant | Émissions de CO₂ rapportées à la population. |
| Taux de natalité | Nombre de naissances rapporté à la population. |
| Scolarisation secondaire | Indicateur de scolarisation dans l'enseignement secondaire. |
| Scolarisation supérieure | Indicateur de scolarisation dans l'enseignement supérieur. |
| Achèvement du primaire | Indicateur d'achèvement de l'enseignement primaire. |
| Dépenses de santé | Dépenses courantes de santé en pourcentage du PIB. |
| Dépenses publiques d'éducation | Dépenses publiques consacrées à l'éducation en pourcentage du PIB. |

## Analyse environnementale et éducative

La page « Environnement & développement » permet notamment d'étudier :

- les émissions de CO₂ par habitant ;
- l'accès à l'électricité ;
- l'achèvement du primaire ;
- les dépenses publiques d'éducation ;
- leur évolution dans le temps ;
- les pays présentant les niveaux de CO₂ par habitant les plus élevés ou les plus faibles.

Les dépenses d'éducation et l'achèvement du primaire peuvent être comparés sur un même graphique afin d'observer leurs évolutions respectives.

Cette comparaison est descriptive et ne permet pas, à elle seule, d'établir une relation de causalité.

## Analyse Machine Learning

La page « Prédiction de l'espérance de vie — 2024 » présente les résultats du modèle de régression linéaire.

Elle permet de comparer :

- l'espérance de vie réellement observée ;
- l'espérance de vie estimée par le modèle ;
- l'erreur absolue de prédiction.

L'erreur absolue correspond à l'écart, en années, entre la valeur observée et la valeur estimée.

Deux niveaux d'analyse peuvent être distingués :

- les performances globales du modèle sur la période de test 2020–2024 ;
- l'analyse spécifique des prédictions affichées pour l'année 2024.

Les données 2024 appartiennent à la période de test du modèle. Elles ne constituent donc pas une prévision d'une année future.

## Performances du modèle

Sur le jeu de test 2020–2024 :

| Indicateur | Résultat |
|---|---:|
| MAE | 2,92 ans |
| RMSE | 3,84 ans |
| R² | 0,7209 |

La MAE représente l'erreur absolue moyenne du modèle sur l'ensemble du jeu de test.

La page Power BI consacrée à 2024 peut afficher une erreur moyenne différente, car elle porte sur une période et éventuellement une population différentes.

## Navigation et filtres

Pour utiliser le tableau de bord :

1. sélectionner si nécessaire une année dans le filtre Année ;
2. sélectionner un pays dans le filtre Pays ;
3. consulter les indicateurs et graphiques associés ;
4. modifier ou supprimer les filtres pour comparer d'autres périodes ou pays.

Lorsqu'un filtre est appliqué, les visualisations concernées sont automatiquement recalculées selon le contexte sélectionné.

## Limites d'interprétation

Les données disponibles varient selon les pays, les années et les indicateurs.

Certaines observations peuvent donc être absentes.

Les comparaisons entre indicateurs montrent des associations et des évolutions mais ne permettent pas, à elles seules, d'établir une relation de causalité.

Les résultats du modèle de Machine Learning sont des estimations statistiques et doivent être interprétés avec les métriques d'évaluation du modèle.

## Contact

Sébastien Nigaize  
Projet Wild Data Hub  
GitHub : `sebastiennigaize-prog/wild-data-hub-dbt`