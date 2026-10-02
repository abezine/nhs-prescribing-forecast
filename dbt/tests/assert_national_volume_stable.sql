-- Warn when national monthly items jump more than 25% month-on-month:
-- usually a partial load or a reclassification, not real demand.
{{ config(severity='warn') }}
with national as (
    select month_start, sum(items) as items
    from {{ ref('fct_prescribing_monthly') }}
    group by 1
),
changes as (
    select
        month_start,
        items,
        items / lag(items) over (order by month_start) - 1 as mom_change
    from national
)
select * from changes where abs(mom_change) > 0.25
