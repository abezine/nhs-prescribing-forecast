-- Modelling table: one row per series x month. Read by the Python forecasting code.
select
    f.series_id,
    f.month_start,
    f.region_code,
    r.region_name,
    f.bnf_chapter_code,
    c.bnf_chapter_name,
    f.items,
    f.total_quantity,
    f.nic_gbp,
    f.actual_cost_gbp,
    f.actual_cost_gbp / nullif(f.items, 0) as cost_per_item_gbp,
    f.is_missing
from {{ ref('int_prescribing__series_month') }} f
left join {{ ref('dim_region') }} r using (region_code)
left join {{ ref('dim_bnf_chapter') }} c using (bnf_chapter_code)
