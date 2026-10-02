-- Fails if an entire month is absent between the first and last loaded month
-- (e.g. a failed API call that fetch_epd.py did not retry).
with loaded as (
    select distinct month_start from {{ ref('stg_epd__region_chapter_month') }}
),
spine as (
    select cast(m as date) as month_start
    from generate_series(
        (select min(month_start) from loaded),
        (select max(month_start) from loaded),
        interval 1 month
    ) as t(m)
)
select s.month_start
from spine s
left join loaded l using (month_start)
where l.month_start is null
