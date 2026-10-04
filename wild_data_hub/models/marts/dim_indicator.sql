select
    indicator_code as indicator_key,
    indicator_code,
    max(indicator_name) as indicator_name

from {{ ref('stg_world_bank') }}

where indicator_code is not null

group by indicator_code