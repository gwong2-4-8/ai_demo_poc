-- Ingram Micro Cloud SQL -> BigQuery Analytics Ingestion & Revenue Summary Mart
-- Region: us-west1 | Dataset: demo1-371900.ingram_micro_analytics

CREATE OR REPLACE TABLE `demo1-371900.ingram_micro_analytics.products`
OPTIONS (
  description = "Ingram Micro master B2B computer hardware catalog replicated from Cloud SQL PostgreSQL (ingram-catalog-sql.ingram_catalog.public.products)."
) AS
SELECT
  sku,
  product_name,
  vendor,
  category,
  CAST(unit_cost_usd AS NUMERIC) AS unit_cost_usd,
  CAST(unit_price_usd AS NUMERIC) AS unit_price_usd,
  active,
  updated_at
FROM EXTERNAL_QUERY(
  "projects/demo1-371900/locations/us-west1/connections/ingram-cloudsql-conn",
  "SELECT sku, product_name, vendor, category, unit_cost_usd, unit_price_usd, active, updated_at FROM public.products;"
);

ALTER TABLE `demo1-371900.ingram_micro_analytics.products`
ALTER COLUMN sku SET OPTIONS (description = "Globally unique Ingram Micro Stock Keeping Unit identifier (IM-<VENDOR>-<MODEL>)."),
ALTER COLUMN product_name SET OPTIONS (description = "Commercial computer hardware model name and configuration."),
ALTER COLUMN vendor SET OPTIONS (description = "OEM hardware brand (Lenovo, Dell, Apple, HP, HPE, NVIDIA, Cisco, Arista, Samsung, Logitech)."),
ALTER COLUMN category SET OPTIONS (description = "B2B product category (Laptops, Enterprise Servers, AI Accelerators, Networking, Storage, Peripherals)."),
ALTER COLUMN unit_cost_usd SET OPTIONS (description = "Distributor wholesale acquisition cost per unit in USD."),
ALTER COLUMN unit_price_usd SET OPTIONS (description = "Standard B2B reseller catalog list price per unit in USD before partner tier discounts.");

CREATE OR REPLACE TABLE `demo1-371900.ingram_micro_analytics.product_transactions`
OPTIONS (
  description = "Ingram Micro B2B reseller order line transactions replicated from Cloud SQL PostgreSQL (ingram-catalog-sql.ingram_catalog.public.product_transactions)."
) AS
SELECT
  transaction_id,
  sku,
  reseller_name,
  sales_region,
  CAST(quantity AS INT64) AS quantity,
  CAST(discount_pct AS NUMERIC) AS discount_pct,
  transaction_ts,
  order_status
FROM EXTERNAL_QUERY(
  "projects/demo1-371900/locations/us-west1/connections/ingram-cloudsql-conn",
  "SELECT transaction_id, sku, reseller_name, sales_region, quantity, discount_pct, transaction_ts, order_status FROM public.product_transactions;"
);

ALTER TABLE `demo1-371900.ingram_micro_analytics.product_transactions`
ALTER COLUMN transaction_id SET OPTIONS (description = "Unique B2B reseller order line transaction identifier."),
ALTER COLUMN sku SET OPTIONS (description = "Catalog SKU ordered by the reseller (joins to products.sku)."),
ALTER COLUMN reseller_name SET OPTIONS (description = "Authorized channel partner / value-added reseller (VAR) name."),
ALTER COLUMN sales_region SET OPTIONS (description = "Geographic sales region (AMER-West, AMER-East, EMEA, APAC)."),
ALTER COLUMN quantity SET OPTIONS (description = "Units ordered on this transaction line."),
ALTER COLUMN discount_pct SET OPTIONS (description = "Partner tier discount percentage off unit_price_usd (0 to 100)."),
ALTER COLUMN transaction_ts SET OPTIONS (description = "UTC timestamp when the reseller order was booked."),
ALTER COLUMN order_status SET OPTIONS (description = "Fulfillment status: COMPLETED, SHIPPED, or RETURNED (RETURNED excluded from recognized revenue).");

CREATE OR REPLACE TABLE `demo1-371900.ingram_micro_analytics.sku_revenue_summary`
OPTIONS (
  description = "Certified Ingram Micro SKU-level B2B revenue and distributor margin summary joining products and fulfilled product_transactions."
) AS
SELECT
  p.sku,
  p.product_name,
  p.vendor,
  p.category,
  p.unit_price_usd,
  p.unit_cost_usd,
  COUNT(t.transaction_id) AS fulfilled_orders,
  SUM(t.quantity) AS units_sold,
  ROUND(SUM(t.quantity * p.unit_price_usd), 2) AS gross_catalog_revenue_usd,
  ROUND(SUM(t.quantity * p.unit_price_usd * (1 - t.discount_pct / 100)), 2) AS net_recognized_revenue_usd,
  ROUND(
    SUM(t.quantity * p.unit_price_usd * (1 - t.discount_pct / 100))
    - SUM(t.quantity * p.unit_cost_usd),
    2
  ) AS distributor_gross_margin_usd
FROM `demo1-371900.ingram_micro_analytics.products` AS p
INNER JOIN `demo1-371900.ingram_micro_analytics.product_transactions` AS t
  ON p.sku = t.sku
WHERE t.order_status IN ('COMPLETED', 'SHIPPED')
GROUP BY
  p.sku,
  p.product_name,
  p.vendor,
  p.category,
  p.unit_price_usd,
  p.unit_cost_usd;
