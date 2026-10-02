-- Latest name per region code (names can change over time)
select region_code, region_name
from {{ ref('stg_epd__region_chapter_month') }}
where not is_unidentified
qualify row_number() over (partition by region_code order by month_start desc) = 1
