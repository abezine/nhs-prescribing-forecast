-- Warn if more than 1% of items in a month cannot be attributed to a region.
{{ config(severity='warn') }}
select
    month_start,
    sum(case when is_unidentified then items else 0 end) * 1.0 / sum(items) as unidentified_share
from {{ ref('stg_epd__region_chapter_month') }}
group by 1
having unidentified_share > 0.01
