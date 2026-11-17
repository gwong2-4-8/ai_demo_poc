---
type: "Metric"
title: "Net Effective Rent Yield"
description: "Annualized net property cash flow after operating expenses and unmitigated hazard remediation reserves divided by estimated asset value."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/metrics/net_effective_rent_yield"
tags: ["cotality", "kpi", "yield", "underwriting"]
status: "stable"
stale_after: "2027-10-30T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T04:00:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T04:05:00Z"
sources:
  - id: "risk-policy"
    resource: "https://github.com/GoogleCloudPlatform/open-knowledge-format"
    title: "Cotality Portfolio Finance & Underwriting Charter FY2026"
    author: "human:cotality_risk_committee"
    last_modified: "2026-10-30T04:00:00Z"
---

# Net Effective Rent Yield

**Net Effective Rent Yield** measures hazard-adjusted annualized return across [Properties Master Table](../tables/properties.md) and prevents overstating yield on parcels with deferred roof or water-intrusion capex [^risk-policy].

## Canonical Business Formula

```text
Net Effective Rent Yield (%) =
  100.0 * (
    (12 * current_monthly_rent_usd * occupancy_factor)
    - annual_operating_expense_usd
    - unmitigated_hazard_reserve_usd
  ) / estimated_asset_value_usd
```

Where per [Property Underwriting & Renewal Guardrail Policy](../policies/property_underwriting_policy.md):
* **Exclusions**: Parcels in `Vacant-Turn` occupancy status are excluded from active stabilized yield rollups (`occupancy_status != 'Vacant-Turn'`).
* **Occupancy Factor**: `0.96` standard economic occupancy allowance (`0.90` when `occupancy_status = 'Notice-Given'`).
* **Unmitigated Hazard Reserve**: Full `est_repair_cost_usd` extracted from multimodal inspection (`urgent_remediation = TRUE`), or `1500` USD baseline reserve when `hazard_risk_score >= 0.70` and no recent roof inspection exists.
* **Attested Implementation**: See [Net Effective Rent Yield SQL](../computations/net_effective_rent_yield_sql.md).
