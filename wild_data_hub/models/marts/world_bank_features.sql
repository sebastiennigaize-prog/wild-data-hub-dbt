-- Une ligne par pays et par année.
-- Les indicateurs explicatifs et la cible proviennent
-- de la table large déjà préparée par dbt.

select
    country_name,
    countryiso3code,
    annee,

    -- Variable à prédire (cible)
    esperance_vie,

    -- Variables explicatives
    pib_par_habitant,
    taux_natalite,
    acces_electricite,
    co2_par_habitant

from {{ ref('mart_country_indicators') }}

-- Pour l'instant, on conserve les NULL et les vrais zéros.
-- Le traitement des valeurs manquantes sera réalisé
-- dans le pipeline scikit-learn, pas dans cette table.