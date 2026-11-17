---
type: "Attested Computation"
title: "Net Effective Rent Yield SQL"
description: "Verified BigQuery GoogleSQL query computing stabilized hazard-adjusted Net Effective Rent Yield by metro_area."
resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/computations/net_effective_rent_yield_sql"
runtime: "bigquery"
parameters:
  - name: "project_id"
    type: "STRING"
    required: true
  - name: "dataset_id"
    type: "STRING"
    required: true
executor:
  resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}"
attester:
  resource: "human:cotality_data_steward"
tags: ["cotality", "attested-sql", "yield"]
status: "stable"
stale_after: "2027-10-30T00:00:00Z"
generated:
  by: "cotality-okf-generator/0.2"
  at: "2026-10-30T04:00:00Z"
verified:
  - by: "human:cotality_data_steward"
    at: "2026-10-30T04:05:00Z"
sources:
  - id: "yield-metric-spec"
    resource: "//bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/cotality_property_ai/metrics/net_effective_rent_yield"
    title: "Net Effective Rent Yield Metric Specification"
    author: "human:cotality_risk_committee"
    last_modified: "2026-10-30T04:00:00Z"
---

# Net Effective Rent Yield — Attested BigQuery SQL

Implements [Net Effective Rent Yield](../metrics/net_effective_rent_yield.md) per [Property Underwriting & Renewal Guardrail Policy](../policies/property_underwriting_policy.md) [^yield-metric-spec].

## Computation

```sql
SELECT
  p.metro_area,
  COUNT(*) AS stabilized_units,
  ROUND(AVG(p.current_monthly_rent_usd), 2) AS avg_in_place_rent_usd,
  ROUND(
    100.0 * SAFE_DIVIDE(
      SUM(
        (12.0 * p.current_monthly_rent_usd * IF(p.occupancy_status = 'Notice-Given', 0.90, 0.96))
        - p.annual_operating_expense_usd
        - COALESCE(img.est_repair_cost_usd, IF(p.hazard_risk_score >= 0.70, 1500.0, 0.0))
      ),
      SUM(p.estimated_asset_value_usd)
    ),
    2
  ) AS net_effective_rent_yield_pct
FROM `${PROJECT_ID}.cotality_property_ai.properties` AS p
LEFT JOIN `${PROJECT_ID}.cotality_property_ai.property_image_assessments` AS img
  ON p.property_id = img.property_id
  AND img.urgent_remediation = TRUE
WHERE p.occupancy_status != 'Vacant-Turn'
GROUP BY p.metro_area
ORDER BY net_effective_rent_yield_pct DESC;
```
