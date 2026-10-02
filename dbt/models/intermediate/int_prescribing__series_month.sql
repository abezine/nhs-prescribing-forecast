-- Complete month x series grid for the chapters in scope.
-- Missing combinations stay NULL and are flagged, never silently zero-filled.
with scoped as (
    select *
    from {{ ref('stg_epd__region_chapter_month') }}
    where not is_unidentified
      and bnf_chapter_code in ('{{ var("include_chapters") | join("','") }}')
),

aggregated as (
    select
        month_start,
        region_code,
        bnf_chapter_code,
        sum(items)           as items,
        sum(total_quantity)  as total_quantity,
        sum(nic_gbp)         as nic_gbp,
        sum(actual_cost_gbp) as actual_cost_gbp
    from scoped
    group by 1, 2, 3
),

month_spine as (
    select cast(m as date) as month_start
    from generate_series(
        (select min(month_start) from aggregated),
        (select max(month_start) from aggregated),
        interval 1 month
    ) as t(m)
),

series as (
    select distinct region_code, bnf_chapter_code from aggregated
)

select
    s.region_code || '_' || s.bnf_chapter_code as series_id,
    m.month_start,
    s.region_code,
    s.bnf_chapter_code,
    a.items,
    a.total_quantity,
    a.nic_gbp,
    a.actual_cost_gbp,
    a.items is null as is_missing
from month_spine m
cross join series s
left join aggregated a
    on a.month_start = m.month_start
   and a.region_code = s.region_code
   and a.bnf_chapter_code = s.bnf_chapter_code
