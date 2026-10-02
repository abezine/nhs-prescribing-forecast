-- Warn on implausible unit costs (GBP per item) that point to unit or parsing errors.
{{ config(severity='warn') }}
select *
from {{ ref('fct_prescribing_monthly') }}
where cost_per_item_gbp is not null
  and (cost_per_item_gbp < 0.5 or cost_per_item_gbp > 5000)
