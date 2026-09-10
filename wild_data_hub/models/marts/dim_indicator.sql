select distinct
    indicator_code as indicator_key,
    indicator_code,
    indicator_name

from {{ ref('stg_world_bank') }}

where indicator_code is not null