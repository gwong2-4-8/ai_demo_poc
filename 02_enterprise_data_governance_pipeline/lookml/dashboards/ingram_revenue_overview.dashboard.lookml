- dashboard: ingram_revenue_overview
  title: Ingram Micro B2B Computer Catalog Revenue & Data Quality Overview
  layout: newspaper
  preferred_viewer: dashboards-next

  elements:
    - name: net_recognized_revenue_kpi
      title: Net Recognized Revenue
      model: ingram_micro_revenue
      explore: product_transactions
      type: single_value
      fields: [product_transactions.net_recognized_revenue]
      limit: 1
      row: 0
      col: 0
      width: 6
      height: 4

    - name: gross_catalog_revenue_kpi
      title: Gross Catalog Revenue
      model: ingram_micro_revenue
      explore: product_transactions
      type: single_value
      fields: [product_transactions.gross_revenue]
      limit: 1
      row: 0
      col: 6
      width: 6
      height: 4

    - name: distributor_gross_margin_kpi
      title: Distributor Gross Margin
      model: ingram_micro_revenue
      explore: product_transactions
      type: single_value
      fields: [product_transactions.distributor_gross_margin]
      limit: 1
      row: 0
      col: 12
      width: 6
      height: 4

    - name: total_units_sold_kpi
      title: Fulfilled Units Sold
      model: ingram_micro_revenue
      explore: product_transactions
      type: single_value
      fields: [product_transactions.total_units_sold]
      limit: 1
      row: 0
      col: 18
      width: 6
      height: 4

    - name: daily_revenue_trend
      title: Daily Net Recognized Revenue Trend
      model: ingram_micro_revenue
      explore: product_transactions
      type: looker_line
      fields: [product_transactions.transaction_date, product_transactions.net_recognized_revenue, product_transactions.gross_revenue]
      sorts: [product_transactions.transaction_date asc]
      limit: 500
      row: 4
      col: 0
      width: 12
      height: 8

    - name: revenue_by_category
      title: Revenue by Hardware Category
      model: ingram_micro_revenue
      explore: product_transactions
      type: looker_column
      fields: [products.category, product_transactions.net_recognized_revenue, product_transactions.distributor_gross_margin]
      sorts: [product_transactions.net_recognized_revenue desc]
      limit: 20
      row: 4
      col: 12
      width: 12
      height: 8

    - name: revenue_by_sku_table
      title: SKU Catalog Pricing & Revenue Performance
      model: ingram_micro_revenue
      explore: product_transactions
      type: looker_grid
      fields: [
        products.sku,
        products.product_name,
        products.vendor,
        products.category,
        products.unit_price_usd,
        product_transactions.total_units_sold,
        product_transactions.gross_revenue,
        product_transactions.net_recognized_revenue,
        product_transactions.distributor_gross_margin
      ]
      sorts: [product_transactions.net_recognized_revenue desc]
      limit: 50
      row: 12
      col: 0
      width: 24
      height: 8

    - name: dq_overall_score_kpi
      title: Data Quality Rule Pass Rate (%)
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: single_value
      fields: [dq_scan_results.overall_dq_score]
      limit: 1
      row: 20
      col: 0
      width: 8
      height: 4

    - name: dq_rules_passed_kpi
      title: DQ Rules Passed
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: single_value
      fields: [dq_scan_results.rules_passed_count]
      limit: 1
      row: 20
      col: 8
      width: 8
      height: 4

    - name: dq_active_alerts_kpi
      title: Active DQ Violations (Alerts)
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: single_value
      fields: [dq_scan_results.rules_failed_count]
      limit: 1
      row: 20
      col: 16
      width: 8
      height: 4

    - name: dq_dimension_pass_chart
      title: Row Pass Rate (%) by DQ Dimension
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: looker_bar
      fields: [dq_scan_results.rule_dimension, dq_scan_results.average_rule_pass_rate_pct]
      sorts: [dq_scan_results.average_rule_pass_rate_pct asc]
      limit: 20
      row: 24
      col: 0
      width: 10
      height: 8

    - name: dq_rule_scorecard_table
      title: Knowledge Catalog Auto Data Quality Scorecard & Remediation SQL
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: looker_grid
      fields: [
        dq_scan_results.table_id,
        dq_scan_results.rule_name,
        dq_scan_results.rule_dimension,
        dq_scan_results.rule_status_label,
        dq_scan_results.rule_rows_evaluated,
        dq_scan_results.rule_rows_passed,
        dq_scan_results.rule_rows_passed_percent,
        dq_scan_results.rule_failed_records_query
      ]
      sorts: [dq_scan_results.rule_rows_passed_percent asc, dq_scan_results.table_id asc]
      limit: 50
      row: 24
      col: 10
      width: 14
      height: 8
