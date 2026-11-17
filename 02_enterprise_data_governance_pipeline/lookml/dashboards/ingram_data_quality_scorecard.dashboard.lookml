- dashboard: ingram_data_quality_scorecard
  title: Ingram Micro Catalog Data Quality Scorecard
  layout: newspaper
  preferred_viewer: dashboards-next

  elements:
    - name: scorecard_dq_score
      title: Overall Rule Pass Rate (%)
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: single_value
      fields: [dq_scan_results.overall_dq_score]
      limit: 1
      row: 0
      col: 0
      width: 6
      height: 4

    - name: scorecard_avg_row_pass
      title: Avg Row Quality (%)
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: single_value
      fields: [dq_scan_results.average_rule_pass_rate_pct]
      limit: 1
      row: 0
      col: 6
      width: 6
      height: 4

    - name: scorecard_rules_passed
      title: Rules Passing Threshold
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: single_value
      fields: [dq_scan_results.rules_passed_count]
      limit: 1
      row: 0
      col: 12
      width: 6
      height: 4

    - name: scorecard_rules_failed
      title: Active Rule Violations
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: single_value
      fields: [dq_scan_results.rules_failed_count]
      limit: 1
      row: 0
      col: 18
      width: 6
      height: 4

    - name: scorecard_by_dimension
      title: Data Quality Pass Rate by Governance Dimension
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: looker_column
      fields: [dq_scan_results.rule_dimension, dq_scan_results.average_rule_pass_rate_pct, dq_scan_results.total_rules_evaluated]
      sorts: [dq_scan_results.average_rule_pass_rate_pct asc]
      limit: 20
      row: 4
      col: 0
      width: 12
      height: 8

    - name: scorecard_by_table
      title: Table-Level Quality Score & Rule Counts
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: looker_bar
      fields: [dq_scan_results.table_id, dq_scan_results.table_quality_score, dq_scan_results.rules_passed_count, dq_scan_results.rules_failed_count]
      sorts: [dq_scan_results.table_quality_score asc]
      limit: 20
      row: 4
      col: 12
      width: 12
      height: 8

    - name: scorecard_audit_detail
      title: Rule-by-Rule Audit Log & Steward Remediation SQL
      model: ingram_micro_revenue
      explore: dq_scan_results
      type: looker_grid
      fields: [
        dq_scan_results.table_id,
        dq_scan_results.rule_name,
        dq_scan_results.rule_dimension,
        dq_scan_results.rule_column,
        dq_scan_results.rule_status_label,
        dq_scan_results.rule_rows_evaluated,
        dq_scan_results.rule_rows_passed,
        dq_scan_results.rule_rows_passed_percent,
        dq_scan_results.rule_description,
        dq_scan_results.rule_failed_records_query
      ]
      sorts: [dq_scan_results.rule_rows_passed_percent asc, dq_scan_results.table_id asc]
      limit: 50
      row: 12
      col: 0
      width: 24
      height: 9
