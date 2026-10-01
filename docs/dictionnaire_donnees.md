# Dictionnaire de données

Ce document décrit les principales tables produites par dbt dans le projet Wild Data Hub.

Les types indiqués correspondent aux types logiques des données utilisées dans BigQuery.

Note : les valeurs de la colonne « Exemple » sont fournies à titre illustratif afin de montrer le format attendu des données.

## dim_pays

Dimension contenant les pays, territoires et agrégats géographiques présents dans les données de la Banque mondiale.

| Colonne | Type | Description | Exemple | Contrainte |
|---|---|---|---|---|
| country_key | STRING | Clé du pays ou de l'entité géographique, basée sur le code ISO3 lorsqu'il est disponible. | FRA | PK logique, non nulle, unique |
| country_name | STRING | Nom du pays, territoire ou agrégat géographique. | France | - |
| countryiso3code | STRING | Code ISO3 ou identifiant géographique fourni par la Banque mondiale. | FRA | Peut être vide selon l'entité |

## dim_annee

Dimension temporelle contenant les années disponibles dans les données.

| Colonne | Type | Description | Exemple | Contrainte |
|---|---|---|---|---|
| annee_key | INTEGER | Clé représentant l'année. | 2024 | PK logique, non nulle, unique |
| annee | INTEGER | Année de l'observation. | 2024 | - |

## dim_indicator

Dimension contenant les indicateurs de la Banque mondiale.

| Colonne | Type | Description | Exemple | Contrainte |
|---|---|---|---|---|
| indicator_key | STRING | Clé de l'indicateur basée sur son code Banque mondiale. | SP.DYN.LE00.IN | PK logique, non nulle, unique |
| indicator_code | STRING | Code officiel de l'indicateur Banque mondiale. | SP.DYN.LE00.IN | - |
| indicator_name | STRING | Libellé de l'indicateur. | Life expectancy at birth, total (years) | - |

## fact_indicators

Table de faits contenant les observations des indicateurs.

Le grain de la table correspond à une combinaison pays, année et indicateur.

| Colonne | Type | Description | Exemple | Contrainte |
|---|---|---|---|---|
| country_key | STRING | Référence vers le pays ou l'entité géographique. | FRA | FK vers `dim_pays`, non nulle |
| annee_key | INTEGER | Référence vers l'année de l'observation. | 2024 | FK vers `dim_annee`, non nulle |
| indicator_key | STRING | Référence vers l'indicateur. | SP.DYN.LE00.IN | FK vers `dim_indicator`, non nulle |
| value | FLOAT | Valeur de l'indicateur pour le pays et l'année. | 82.4 | Peut être nulle |

La combinaison `country_key + annee_key + indicator_key` constitue l'identifiant logique d'une observation.

## mart_country_indicators

Table analytique au format large contenant une ligne par pays et par année.

| Colonne | Type | Description | Exemple |
|---|---|---|---|
| country_name | STRING | Nom du pays ou de l'entité géographique. | France |
| countryiso3code | STRING | Code ISO3 ou identifiant géographique. | FRA |
| annee | INTEGER | Année de l'observation. | 2024 |
| pib | FLOAT | Produit intérieur brut. | 3000000000000 |
| pib_par_habitant | FLOAT | PIB par habitant. | 44000 |
| croissance_pib | FLOAT | Taux de croissance annuel du PIB. | 1.2 |
| population | FLOAT | Population totale. | 68000000 |
| esperance_vie | FLOAT | Espérance de vie à la naissance, en années. | 82.4 |
| chomage | FLOAT | Taux de chômage. | 7.4 |
| inflation | FLOAT | Taux d'inflation. | 2.0 |
| acces_electricite | FLOAT | Part de la population ayant accès à l'électricité, en %. | 100 |
| co2_par_habitant | FLOAT | Émissions de CO₂ par habitant. | 4.0 |
| taux_natalite | FLOAT | Taux de natalité. | 10.7 |
| scolarisation_secondaire | FLOAT | Taux de scolarisation dans le secondaire. | 110 |
| scolarisation_superieur | FLOAT | Taux de scolarisation dans l'enseignement supérieur. | 70 |
| achevement_primaire | FLOAT | Taux d'achèvement du primaire. | 99 |
| depense_de_sante | FLOAT | Dépenses courantes de santé en pourcentage du PIB. | 12 |
| depense_publique_education | FLOAT | Dépenses publiques d'éducation en pourcentage du PIB. | 5 |
| alphabetisation_adultes | FLOAT | Taux d'alphabétisation des adultes. | 99 |

## world_bank_features

Table préparant les variables utilisées par le modèle de Machine Learning.

| Colonne | Type | Description | Exemple | Utilisation ML |
|---|---|---|---|---|
| country_name | STRING | Nom du pays ou de l'entité géographique. | France | Identification |
| countryiso3code | STRING | Code ISO3 ou identifiant géographique. | FRA | Identification |
| annee | INTEGER | Année de l'observation. | 2024 | Découpage chronologique |
| esperance_vie | FLOAT | Espérance de vie à la naissance. | 82.4 | Variable cible |
| pib_par_habitant | FLOAT | PIB par habitant. | 44000 | Variable explicative |
| taux_natalite | FLOAT | Taux de natalité. | 10.7 | Variable explicative |
| acces_electricite | FLOAT | Accès à l'électricité en pourcentage de la population. | 100 | Variable explicative |
| co2_par_habitant | FLOAT | Émissions de CO₂ par habitant. | 4.0 | Variable explicative |

Les valeurs manquantes des variables explicatives ne sont pas supprimées dans cette table. Elles sont traitées dans le pipeline scikit-learn par une imputation utilisant la médiane.