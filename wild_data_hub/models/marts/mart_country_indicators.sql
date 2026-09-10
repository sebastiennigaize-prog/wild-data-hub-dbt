select
    country_name,
    countryiso3code,
    annee,

    max(case when indicator_code = 'NY.GDP.MKTP.CD' then value end) as pib,
    max(case when indicator_code = 'NY.GDP.PCAP.CD' then value end) as pib_par_habitant,
    max(case when indicator_code = 'NY.GDP.MKTP.KD.ZG' then value end) as croissance_pib,
    max(case when indicator_code = 'SP.POP.TOTL' then value end) as population,
    max(case when indicator_code = 'SP.DYN.LE00.IN' then value end) as esperance_vie,
    max(case when indicator_code = 'SL.UEM.TOTL.ZS' then value end) as chomage,
    max(case when indicator_code = 'FP.CPI.TOTL.ZG' then value end) as inflation,
    max(case when indicator_code = 'EG.ELC.ACCS.ZS' then value end) as acces_electricite,
    max(case when indicator_code = 'EN.GHG.CO2.PC.CE.AR5' then value end) as co2_par_habitant,
    max(case when indicator_code = 'SP.DYN.CBRT.IN' then value end) as taux_natalite,
    max(case when indicator_code = 'SE.SEC.ENRR' then value end) as scolarisation_secondaire,
    max(case when indicator_code = 'SE.TER.ENRR' then value end) as scolarisation_superieur,
    max(case when indicator_code = 'SE.PRM.CMPT.ZS' then value end) as achevement_primaire,
    max(case when indicator_code = 'SH.XPD.CHEX.GD.ZS' then value end) as depense_de_sante,
    max(case when indicator_code = 'SE.XPD.TOTL.GD.ZS' then value end) as depense_publique_education,
    max(case when indicator_code = 'SE.ADT.LITR.ZS' then value end) as alphabetisation_adultes

from {{ ref('stg_world_bank') }}

group by
    country_name,
    countryiso3code,
    annee