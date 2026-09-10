with ranked_observations as (

    select
        case
            when trim(countryiso3code) != '' then countryiso3code
            else country_name
        end as country_key,

        annee as annee_key,
        indicator_code as indicator_key,
        value,
        inserted_at,

        row_number() over (
            partition by
                case
                    when trim(countryiso3code) != '' then countryiso3code
                    else country_name
                end,
                annee,
                indicator_code
            order by inserted_at desc
        ) as row_num

    from {{ ref('stg_world_bank') }}

    where country_name is not null
      and annee is not null
      and indicator_code is not null

)

select
    country_key,
    annee_key,
    indicator_key,
    value

from ranked_observations

where row_num = 1