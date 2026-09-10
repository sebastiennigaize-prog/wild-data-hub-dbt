select distinct
    case
        when trim(countryiso3code) != '' then countryiso3code
        else country_name
    end as country_key,

    country_name,
    countryiso3code

from {{ ref('stg_world_bank') }}

where country_name is not null