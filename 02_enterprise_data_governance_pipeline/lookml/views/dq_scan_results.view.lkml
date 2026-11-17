view: dq_scan_results {
  sql_table_name: `demo1-371900.ingram_micro_analytics.dq_scan_results` ;;

  dimension: job_rule_pk {
    primary_key: yes
    hidden: yes
    type: string
    sql: CONCAT(${TABLE}.data_quality_job_id, '::', COALESCE(${TABLE}.rule_name, '')) ;;
    description: "Composite primary key combining Dataplex data_quality_job_id and rule_name"
  }

  dimension: data_quality_job_id {
    type: string
    sql: ${TABLE}.data_quality_job_id ;;
    description: "Unique execution job ID of the Knowledge Catalog Auto Data Quality scan"
  }

  dimension: data_scan_id {
    type: string
    sql: ${TABLE}.data_quality_scan.data_scan_id ;;
    description: "Knowledge Catalog DataScan resource identifier"
  }

  dimension: table_id {
    type: string
    sql: ${TABLE}.data_source.table_id ;;
    description: "Validated BigQuery table name (products or product_transactions)"
  }

  dimension_group: job_start {
    type: time
    timeframes: [raw, time, date, week, month]
    sql: ${TABLE}.job_start_time ;;
    description: "UTC start timestamp of the Data Quality scan run"
  }

  dimension: job_overall_score {
    type: number
    value_format_name: decimal_1
    sql: ${TABLE}.job_quality_result.score ;;
    description: "Table-level overall data quality score (0 to 100) reported by Knowledge Catalog"
  }

  dimension: rule_name {
    type: string
    sql: ${TABLE}.rule_name ;;
    description: "Declarative Data Quality rule identifier"
  }

  dimension: rule_description {
    type: string
    sql: ${TABLE}.rule_description ;;
    description: "Business description of the Data Quality expectation"
  }

  dimension: rule_dimension {
    type: string
    sql: ${TABLE}.rule_dimension ;;
    description: "Data Quality governance dimension (COMPLETENESS, UNIQUENESS, VALIDITY, CONSISTENCY, INTEGRITY)"
  }

  dimension: rule_column {
    type: string
    sql: COALESCE(${TABLE}.rule_column, 'table-level') ;;
    description: "Target column evaluated by the Data Quality rule"
  }

  dimension: rule_type {
    type: string
    sql: ${TABLE}.rule_type ;;
    description: "Built-in or custom SQL expectation type"
  }

  dimension: rule_passed {
    type: yesno
    sql: ${TABLE}.rule_passed ;;
    description: "Whether the Data Quality rule met its passing threshold"
  }

  dimension: rule_status_label {
    type: string
    sql: CASE WHEN ${TABLE}.rule_passed THEN 'PASS' ELSE 'ALERT: VIOLATION' END ;;
    description: "Human-readable PASS or ALERT: VIOLATION badge for scorecard tables"
  }

  dimension: rule_rows_evaluated {
    type: number
    sql: ${TABLE}.rule_rows_evaluated ;;
    description: "Number of rows evaluated by this rule"
  }

  dimension: rule_rows_passed {
    type: number
    sql: ${TABLE}.rule_rows_passed ;;
    description: "Number of rows satisfying this rule"
  }

  dimension: rule_rows_passed_percent {
    type: number
    value_format_name: decimal_2
    sql: ${TABLE}.rule_rows_passed_percent ;;
    description: "Percentage of evaluated rows passing this rule (0 to 100)"
  }

  dimension: rule_failed_records_query {
    type: string
    sql: COALESCE(${TABLE}.rule_failed_records_query, 'No failing rows (100% pass)') ;;
    description: "Auto-generated BigQuery SQL query to inspect failing records for steward remediation"
  }

  measure: total_rules_evaluated {
    type: count
    description: "Total Data Quality rules evaluated across latest table scans"
  }

  measure: rules_passed_count {
    type: count
    filters: [rule_passed: "yes"]
    description: "Count of Data Quality rules passing threshold"
  }

  measure: rules_failed_count {
    type: count
    filters: [rule_passed: "no"]
    description: "Count of Data Quality rules failing threshold (active DQ alerts)"
  }

  measure: average_rule_pass_rate_pct {
    type: average
    value_format_name: decimal_1
    sql: ${rule_rows_passed_percent} ;;
    description: "Average row-level pass percentage across evaluated Data Quality rules (0 to 100)"
  }

  measure: table_quality_score {
    type: max
    value_format_name: decimal_1
    sql: ${TABLE}.job_quality_result.score ;;
    description: "Table-level overall quality score (0 to 100) reported by Knowledge Catalog"
  }

  measure: overall_dq_score {
    type: number
    value_format_name: decimal_1
    sql: ROUND(100.0 * SAFE_DIVIDE(${rules_passed_count}, NULLIF(${total_rules_evaluated}, 0)), 1) ;;
    description: "Percentage of Data Quality rules passing across Ingram Micro catalog tables"
  }
}
