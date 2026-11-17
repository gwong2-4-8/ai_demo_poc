view: products {
  sql_table_name: `demo1-371900.ingram_micro_analytics.products` ;;

  dimension: sku {
    primary_key: yes
    type: string
    sql: ${TABLE}.sku ;;
    description: "Globally unique Ingram Micro Stock Keeping Unit identifier (IM-<VENDOR>-<MODEL>)"
  }

  dimension: product_name {
    type: string
    sql: ${TABLE}.product_name ;;
    description: "Commercial computer hardware model name and configuration"
  }

  dimension: vendor {
    type: string
    sql: ${TABLE}.vendor ;;
    description: "Original Equipment Manufacturer (OEM) hardware brand"
  }

  dimension: category {
    type: string
    sql: ${TABLE}.category ;;
    description: "IT distribution product category (Laptops, Enterprise Servers, AI Accelerators, Networking, Storage, Peripherals)"
  }

  dimension: unit_cost_usd {
    type: number
    value_format_name: usd
    sql: ${TABLE}.unit_cost_usd ;;
    description: "Distributor wholesale acquisition cost per unit in USD"
  }

  dimension: unit_price_usd {
    type: number
    value_format_name: usd
    sql: ${TABLE}.unit_price_usd ;;
    description: "Standard B2B reseller catalog list price per unit in USD before partner discounts"
  }

  dimension: active {
    type: yesno
    sql: ${TABLE}.active ;;
    description: "Whether the SKU is active in the Ingram Micro catalog"
  }

  dimension_group: updated {
    type: time
    timeframes: [raw, time, date, week, month, year]
    sql: ${TABLE}.updated_at ;;
    description: "Timestamp when the catalog SKU record was last updated"
  }

  measure: sku_count {
    type: count
    description: "Total distinct SKUs in the Ingram Micro computer catalog"
  }

  measure: average_list_price {
    type: average
    value_format_name: usd
    sql: ${unit_price_usd} ;;
    description: "Average catalog list price (USD) across SKUs"
  }
}
