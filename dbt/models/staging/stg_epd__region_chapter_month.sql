-- One row per month x region x BNF chapter as delivered by the API.
-- Normalises types, splits the combined chapter field, flags unattributable rows.
with source as (
    select * from {{ source('epd', 'epd') }}
)

select
    strptime(replace(cast(YEAR_MONTH as varchar), '-', '') || '01', '%Y%m%d')::date as month_start,
    nullif(trim(REGIONAL_OFFICE_CODE), '-')                          as region_code,
    upper(trim(REGIONAL_OFFICE_NAME))                                 as region_name,
    trim(split_part(BNF_CHAPTER_PLUS_CODE, ':', 1))                   as bnf_chapter_code,
    trim(substr(BNF_CHAPTER_PLUS_CODE, strpos(BNF_CHAPTER_PLUS_CODE, ':') + 1)) as bnf_chapter_name,
    cast(ITEMS as bigint)                                             as items,
    cast(TOTAL_QUANTITY as double)                                    as total_quantity,
    cast(NIC as double)                                               as nic_gbp,
    cast(ACTUAL_COST as double)                                       as actual_cost_gbp,
    cast(SOURCE_ROWS as bigint)                                       as source_rows,
    (
        REGIONAL_OFFICE_CODE is null
        or trim(REGIONAL_OFFICE_CODE) in ('', '-')
        or upper(REGIONAL_OFFICE_NAME) like '%UNIDENTIFIED%'
    )                                                                 as is_unidentified,
    _SOURCE_RESOURCE                                                  as source_resource
from source
