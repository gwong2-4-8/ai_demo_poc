view: product_transactions {
  sql_table_name: `demo1-371900.ingram_micro_analytics.product_transactions` ;;

  dimension: transaction_id {
    primary_key: yes
    type: string
    sql: ${TABLE}.transaction_id ;;
    description: "Unique B2B reseller purchase order line transaction ID"
  }

  dimension: sku {
    type: string
    sql: ${TABLE}.sku ;;
    description: "Catalog SKU ordered on this transaction line"
  }

  dimension: reseller_name {
    type: string
    sql: ${TABLE}.reseller_name ;;
    description: "Authorized channel partner or value-added reseller (VAR) name"
  }

  dimension: sales_region {
    type: string
    sql: ${TABLE}.sales_region ;;
    description: "Geographic distribution sales region (AMER-West, AMER-East, EMEA, APAC)"
  }

  dimension: quantity {
    type: number
    sql: ${TABLE}.quantity ;;
    description: "Number of hardware units ordered on this transaction line"
  }

  dimension: discount_pct {
    type: number
    value_format_name: decimal_2
    sql: ${TABLE}.discount_pct ;;
    description: "Partner tier discount percentage off catalog unit list price (0 to 100)"
  }

  dimension: order_status {
    type: string
    sql: ${TABLE}.order_status ;;
    description: "Fulfillment lifecycle status (COMPLETED, SHIPPED, or RETURNED)"
  }

  dimension_group: transaction {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.transaction_ts ;;
    description: "UTC timestamp when the B2B reseller transaction was booked"
  }

  dimension: line_gross_amount {
    type: number
    value_format_name: usd
    sql: ${quantity} * ${products.unit_price_usd} ;;
    description: "Line-item gross catalog value before partner discounts (quantity * unit_price_usd)"
  }

  dimension: line_net_revenue_amount {
    type: number
    value_format_name: usd
    sql: ${quantity} * ${products.unit_price_usd} * (1 - (${discount_pct} / 100.0)) ;;
    description: "Line-item net revenue after partner discount percentage"
  }

  dimension: line_cogs_amount {
    type: number
    value_format_name: usd
    sql: ${quantity} * ${products.unit_cost_usd} ;;
    description: "Line-item distributor cost of goods sold (quantity * unit_cost_usd)"
  }

  measure: transaction_count {
    type: count
    description: "Total count of transaction lines (all statuses)"
  }

  measure: fulfilled_order_count {
    type: count
    filters: [order_status: "COMPLETED, SHIPPED"]
    description: "Count of fulfilled reseller transaction lines (COMPLETED and SHIPPED)"
  }

  measure: total_units_sold {
    type: sum
    sql: ${quantity} ;;
    filters: [order_status: "COMPLETED, SHIPPED"]
    description: "Total hardware units sold across COMPLETED and SHIPPED orders"
  }

  measure: gross_revenue {
    type: sum
    value_format_name: usd
    sql: ${line_gross_amount} ;;
    filters: [order_status: "COMPLETED, SHIPPED"]
    description: "Gross Catalog Revenue (USD) before partner discounts across COMPLETED and SHIPPED orders"
  }

  measure: net_recognized_revenue {
    type: sum
    value_format_name: usd
    sql: ${line_net_revenue_amount} ;;
    filters: [order_status: "COMPLETED, SHIPPED"]
    description: "Net Recognized Revenue (USD) after partner tier discounts across COMPLETED and SHIPPED orders"
  }

  measure: total_cogs {
    type: sum
    value_format_name: usd
    sql: ${line_cogs_amount} ;;
    filters: [order_status: "COMPLETED, SHIPPED"]
    description: "Total distributor Cost of Goods Sold (USD) across COMPLETED and SHIPPED orders"
  }

  measure: distributor_gross_margin {
    type: number
    value_format_name: usd
    sql: ${net_recognized_revenue} - ${total_cogs} ;;
    description: "Distributor Gross Margin (USD): Net Recognized Revenue minus Total COGS"
  }
}
