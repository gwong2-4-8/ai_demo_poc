# Ingram Micro B2B Catalog & Revenue Recognition Standard Operating Procedure (SOP)

## 1. Domain Overview
Ingram Micro distributes commercial computer hardware, AI accelerators, enterprise servers, networking switches, storage, and peripherals to authorized Value-Added Resellers (VARs) across `AMER-West`, `AMER-East`, `EMEA`, and `APAC`.

## 2. Authoritative Data Sources & Join Rules
- **Master Catalog (`products`)**: Stored operationally in Cloud SQL for PostgreSQL (`ingram-catalog-sql.ingram_catalog.public.products`) and replicated to BigQuery (`demo1-371900.ingram_micro_analytics.products`). Primary key is `sku` (formatted `IM-<VENDOR>-<MODEL>`).
- **Reseller Transactions (`product_transactions`)**: Stored in Cloud SQL (`public.product_transactions`) and replicated to BigQuery (`demo1-371900.ingram_micro_analytics.product_transactions`). Joins many-to-one onto `products` via `product_transactions.sku = products.sku`.

## 3. Certified Revenue & Margin Formulas
1. **Fulfillment Status Filter (Mandatory)**: Always filter `order_status IN ('COMPLETED', 'SHIPPED')` when calculating recognized revenue, COGS, or units sold. Orders with `order_status = 'RETURNED'` represent RMA returns and must be excluded from recognized revenue.
2. **Gross Catalog Revenue (`gross_revenue`)**:
   `SUM(quantity * unit_price_usd)` where `order_status IN ('COMPLETED', 'SHIPPED')`.
3. **Net Recognized Revenue (`net_recognized_revenue`)**:
   `SUM(quantity * unit_price_usd * (1 - discount_pct / 100.0))` where `order_status IN ('COMPLETED', 'SHIPPED')`.
4. **Distributor Gross Margin (`distributor_gross_margin`)**:
   `Net Recognized Revenue - SUM(quantity * unit_cost_usd)` where `order_status IN ('COMPLETED', 'SHIPPED')`.

## 4. Verified Golden SQL Query
```sql
SELECT
  p.category,
  p.vendor,
  SUM(t.quantity) AS units_sold,
  ROUND(SUM(t.quantity * p.unit_price_usd), 2) AS gross_catalog_revenue_usd,
  ROUND(SUM(t.quantity * p.unit_price_usd * (1 - t.discount_pct / 100)), 2) AS net_recognized_revenue_usd,
  ROUND(
    SUM(t.quantity * p.unit_price_usd * (1 - t.discount_pct / 100)) - SUM(t.quantity * p.unit_cost_usd),
    2
  ) AS distributor_gross_margin_usd
FROM `demo1-371900.ingram_micro_analytics.product_transactions` AS t
INNER JOIN `demo1-371900.ingram_micro_analytics.products` AS p
  ON t.sku = p.sku
WHERE t.order_status IN ('COMPLETED', 'SHIPPED')
GROUP BY p.category, p.vendor
ORDER BY net_recognized_revenue_usd DESC;
```

## 5. Automated Data Quality Governance (`dq_scan_results`)
Ingram Micro enforces 10 declarative Knowledge Catalog Auto Data Quality rules across `products` (`ingram-products-dq-scan`) and `product_transactions` (`ingram-transactions-dq-scan`) across five governance dimensions (`COMPLETENESS`, `UNIQUENESS`, `VALIDITY`, `CONSISTENCY`, `INTEGRITY`):
1. **B2B Margin Floor Guardrail (`margin-floor-guardrail`)**: Every SKU in `products` must satisfy `unit_price_usd >= unit_cost_usd` (`100%` threshold). Any draft or active SKU priced below wholesale cost triggers an active violation badge in Knowledge Catalog and exports an auto-generated steward remediation query (`rule_failed_records_query`) to `demo1-371900.ingram_micro_analytics.dq_scan_results`.
2. **Order & Discount Guardrails**: Reseller orders in `product_transactions` must reference a valid catalog `sku` (`catalog-sku-referential-integrity`), maintain `discount_pct` between `0%` and `25%` (`partner-discount-cap`), and belong to governed fulfillment states (`COMPLETED`, `SHIPPED`, `RETURNED`).
3. **Executive & Steward Monitoring**: All scan runs automatically publish table quality scores (`job_quality_result.score`) to Knowledge Catalog and stream row-level metrics into Looker **Dashboard #4** (*Executive Revenue & Data Quality Overview*) and **Dashboard #5** (*Catalog Data Quality Scorecard*).
