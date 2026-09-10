select
    country_key,
    annee_key,
    indicator_key,
    count(*) as nombre_lignes

from {{ ref('fact_indicators') }}

group by
    country_key,
    annee_key,
    indicator_key

having count(*) > 1