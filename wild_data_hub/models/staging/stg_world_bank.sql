with source as (

    select *
    from {{ source('world_bank', 'raw_data') }}

),

staging as (

    select
        data.country.value as country_name,
        data.countryiso3code as countryiso3code,
        safe_cast(data.date as int64) as annee,

        data.indicator.id as indicator_code,
        data.indicator.value as indicator_name,
        data.value as value,
        data.unit as unit,
        data.obs_status as obs_status,
        data.decimal as decimal,

        row_hash,
        inserted_at

    from source

)

select *
from staging