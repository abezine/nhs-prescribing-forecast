select bnf_chapter_code, bnf_chapter_name
from {{ ref('stg_epd__region_chapter_month') }}
qualify row_number() over (partition by bnf_chapter_code order by month_start desc) = 1
