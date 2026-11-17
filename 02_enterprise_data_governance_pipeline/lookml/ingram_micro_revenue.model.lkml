connection: "ingram_micro_bq"

include: "/views/products.view.lkml"
include: "/views/product_transactions.view.lkml"
include: "/views/dq_scan_results.view.lkml"
include: "/dashboards/**/*.dashboard.lookml"

explore: product_transactions {
  label: "Ingram Micro Catalog & Revenue"
  description: "B2B computer hardware catalog orders joined with master SKU pricing to calculate Gross Revenue, Net Recognized Revenue, and Distributor Margin."

  join: products {
    type: left_outer
    relationship: many_to_one
    sql_on: ${product_transactions.sku} = ${products.sku} ;;
  }
}

explore: dq_scan_results {
  label: "Ingram Micro Data Quality Scorecard"
  description: "Latest Knowledge Catalog (Dataplex) Auto Data Quality rule evaluations, dimension pass rates, and remediation SQL across Ingram Micro BigQuery tables."

  sql_always_where: ${data_quality_job_id} IN (
    SELECT AS VALUE ARRAY_AGG(data_quality_job_id ORDER BY job_start_time DESC LIMIT 1)[OFFSET(0)]
    FROM `demo1-371900.ingram_micro_analytics.dq_scan_results`
    GROUP BY data_source.table_id
  ) ;;
}
