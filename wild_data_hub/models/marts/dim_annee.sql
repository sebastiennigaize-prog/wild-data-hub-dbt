select distinct
    annee as annee_key,
    annee

from {{ ref('stg_world_bank') }}

where annee is not null