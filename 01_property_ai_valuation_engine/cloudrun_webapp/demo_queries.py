# Copyright 2026 Google LLC
# SPDX-License-Identifier: Apache-2.0
"""SQL queries, presenter talk tracks, and Open Knowledge Format builder for Cotality Demo."""

from pathlib import Path
from typing import Dict

# ---------------------------------------------------------------------------
# Presenter Talk Tracks & Key Value Takeaways (from Cotality_property_trend_demo_talk_track.md)
# ---------------------------------------------------------------------------
TALK_TRACKS: Dict[str, Dict[str, str]] = {
    "overview": {
        "title": "Opening Pitch (60 Seconds) — Zero-ETL AI & ML Directly in BigQuery",
        "narrative": (
            "Today we are going to walk through an end-to-end residential property valuation, "
            "market trend forecasting, and multimodal listing inspection pipeline—built 100% inside "
            "BigQuery using standard SQL. Historically, building this required stitching together "
            "four separate systems: a vision pipeline to inspect exterior property photos in Cloud Storage, "
            "an NLP pipeline to read listing descriptions, a time-series training cluster to forecast metro "
            "price and rent trajectories, and a custom XGBoost pipeline to value comparable properties. "
            "Everything stays in BigQuery across three clean tables: properties, sold_and_rent_history, "
            "and property_comps."
        ),
        "takeaway": (
            "Zero data movement, governed SQL execution, and four foundation model capabilities "
            "(Gemini, ObjectRef Multimodal, TimesFM, and TabFM) operating directly where the data lives."
        ),
        "qa_tip": (
            "How does BigQuery handle billing and governance for these AI calls? Every AI.GENERATE, "
            "AI.IF, AI.CLASSIFY, AI.FORECAST, and AI.PREDICT call executes through governed BigQuery "
            "and Vertex AI endpoints, subject to standard IAM, BigQuery slot reservations, and quota controls."
        ),
    },
    "tab1_foundation": {
        "title": "Steps 1 & 2 Talk Track — Partitioned & Clustered Data Foundation + ML.DESCRIBE_DATA",
        "narrative": (
            "Notice how the 3 core tables are engineered for scale: sold_and_rent_history (360 rows = "
            "5 metros × 72 months from 2020–2025) is partitioned by month_date and clustered by metro_area. "
            "properties (100 active listings, including 6 featured properties PROP-101 to PROP-106 with "
            "CC0 exterior photos in GCS) and property_comps (240 historical sales/rentals: 190 TRAIN, "
            "50 VALIDATION) are clustered by metro_area, property_type. Before running any AI or ML, "
            "ML.DESCRIBE_DATA profiles completeness, min, max, and medians in a single SQL statement."
        ),
        "takeaway": (
            "Instant single-statement data profiling across numeric features without "
            "exporting data to Pandas or spinning up Spark clusters."
        ),
        "qa_tip": (
            "Partitioning on month_date and clustering on metro_area ensures time-series horizon windows "
            "and metro-level joins prune unnecessary blocks automatically."
        ),
    },
    "tab2_okf": {
        "title": "Step 3 Talk Track — Open Knowledge Format Grounding vs. Ungrounded Text-to-SQL",
        "narrative": (
            "Why do generic Text-to-SQL demos fail in enterprise real estate? Because a database schema "
            "tells an LLM what columns exist (sold_price_usd, monthly_rent_usd, is_fixer_upper), but "
            "never encodes institutional valuation methodology. When we ask for Effective Gross Rental Yield (%) "
            "by metro area: in 1a (Ungrounded), Gemini only sees raw column names—it averages "
            "raw row-level ratios, forgets the 5% vacancy allowance, and includes distressed fixer-uppers. "
            "In 1b (Open Knowledge Format Grounded), we ground Gemini in portable Markdown + YAML semantic "
            "files that enforce is_fixer_upper = FALSE, the 0.95 collection factor, and portfolio-weighted SAFE_DIVIDE."
        ),
        "takeaway": (
            "Eliminates metric drift. The Open Knowledge Format lives in Git alongside your pipelines—any "
            "SQL agent or analyst in BigQuery uses the exact same attested business definition."
        ),
        "qa_tip": (
            "Why use Markdown + YAML instead of hardcoding prompts in Python? Markdown + YAML is "
            "human-readable for data stewards, version-controlled in Git, and tool-agnostic across "
            "BigQuery Studio, Cloud Run apps, and BI tools."
        ),
    },
    "tab3_multimodal": {
        "title": "Step 4 Talk Track — Multimodal Photo Inspection with ObjectRef & AI.GENERATE",
        "narrative": (
            "Property condition lives in photos, not just tabular columns. Normally, extracting structured "
            "curb-appeal scores or roof/siding condition from photos in Cloud Storage requires custom vision "
            "endpoints and JSON ETL pipelines. Here, we use OBJ.MAKE_REF(p.gcs_image_uri, 'us.cotality-conn') "
            "and OBJ.FETCH_METADATA to pass live GCS image references directly into AI.GENERATE inside "
            "a CREATE OR REPLACE TABLE statement with a strongly typed output_schema."
        ),
        "takeaway": (
            "Unstructured property photos in Cloud Storage become strongly-typed relational columns "
            "(architectural_style, exterior_condition, curb_appeal_score, visible_features, photo_summary) "
            "in one SQL query—ready to join with comps and forecasts."
        ),
        "qa_tip": (
            "Does BigQuery copy the images into table storage? No—ObjectRef stores lightweight metadata "
            "pointers to gs://cotality-workshop/... and streams bytes securely via the Cloud Resource Connection."
        ),
    },
    "tab4_screening": {
        "title": "Step 5 Talk Track — Semantic Listing Screening (AI.IF & AI.CLASSIFY)",
        "narrative": (
            "Every property table has unstructured MLS listing remarks (listing_notes). Historically, data engineers wrote "
            "hundreds of brittle REGEXP_CONTAINS or LIKE '%tlc%' clauses that broke on negations like "
            "'needs no work' or 'roof replaced in 2024'. With AI.IF, we filter and flag listings using "
            "plain English and few-shot examples in SQL—returning a native BOOL column (is_move_in_ready). With AI.CLASSIFY, "
            "we bucket listings into canonical buyer segments (Turnkey Family Home, Luxury Residence, "
            "Fixer-Upper / Value-Add, Starter / Cozy Home) with zero training data."
        ),
        "takeaway": (
            "Replaces fragile regex rules with semantic SQL primitives (AI.IF, AI.CLASSIFY) that return "
            "native BigQuery BOOL and STRING types and chain directly into downstream ML models."
        ),
        "qa_tip": (
            "Notice how Step 5's AI.IF output (is_move_in_ready) is inverted in Step 7 "
            "(NOT is_move_in_ready AS is_fixer_upper) and fed directly as a feature into TabFM!"
        ),
    },
    "tab5_forecast": {
        "title": "Step 6 Talk Track — Zero-Training Metro Price & Rent Forecasting (TimesFM)",
        "narrative": (
            "Next, we want to know where each metro market is heading over the next 12 months. In the past, "
            "you had to run CREATE MODEL with ARIMA_PLUS and manage model artifacts per metric. With "
            "BigQuery's built-in TimesFM time-series foundation model, we forecast all 5 metros in parallel "
            "using id_cols => ['metro_area']—with zero model training. First, we run AI.EVALUATE on a "
            "12-month holdout window (2025) to prove backtest MAPE (~1.3%–1.9%), then generate 12-month "
            "forward forecasts with 95% confidence bounds via AI.FORECAST."
        ),
        "takeaway": (
            "Zero-shot multi-series forecasting across all metro markets for both Median Sold Price and "
            "Average Monthly Rent, complete with holdout backtest evaluation and 95% prediction intervals."
        ),
        "qa_tip": (
            "Setting output_historical_time_series => TRUE returns the 72 months of historical data "
            "and 12 months of forecast rows in a single table for seamless visualization."
        ),
    },
    "tab6_tabfm": {
        "title": "Step 7 Talk Track — Zero-Shot Comparable Property Valuation (TabFM)",
        "narrative": (
            "How do we estimate fair-market sold price and monthly rent for each individual property "
            "based on our 240 historical comps—without waiting 30 minutes to train and tune an XGBoost model? "
            "BigQuery's AI.PREDICT uses Google's Tabular Foundation Model (TabFM) for in-context tabular "
            "learning. In a single SQL query, we pass the historical comps as the context table and our "
            "active properties—enriched with Step 5's NOT is_move_in_ready AS is_fixer_upper flag—as the "
            "prediction input. We first validate accuracy with AI.EVALUATE on the 50-row VALIDATION split."
        ),
        "takeaway": (
            "Instant, training-free Automated Valuation Model (AVM) for both sold price and monthly rent, "
            "chaining LLM-extracted text features (AI.IF) directly into tabular foundation model inference."
        ),
        "qa_tip": (
            "How does TabFM work without CREATE MODEL? TabFM performs in-context learning at query time: "
            "it reads the 190 TRAIN comp feature/label distributions in memory and predicts target values "
            "for the evaluation rows in seconds."
        ),
    },
    "tab7_unified": {
        "title": "Step 8 Talk Track — Unified Property Valuation Cards (The Grand Finale)",
        "narrative": (
            "Finally, let's bring all four AI & ML modalities together into a single SQL query for our "
            "6 featured properties (PROP-101 to PROP-106). In one SELECT statement, we join: "
            "(1) TabFM comp valuations (comp_predicted_sold_usd, comp_predicted_rent_usd, and okf_effective_yield_pct), "
            "(2) Multimodal photo insights (curb_appeal_score & exterior_condition from GCS images), "
            "(3) Seller screening & buyer segment (AI.IF & AI.CLASSIFY), and "
            "(4) TimesFM 12-month metro appreciation trajectory—then call AI.GENERATE with a structured "
            "schema to synthesize an executive recommendation_tag and 2-sentence analyst_valuation_brief."
        ),
        "takeaway": (
            "The ultimate BigQuery value proposition: Tabular ML + Time-Series Forecasting + Multimodal "
            "Vision + Generative AI synthesis joined in a single governed SQL query."
        ),
        "qa_tip": (
            "Notice how PROP-106 (Austin fixer-upper) automatically gets flagged with roof/siding condition "
            "warnings and a lower TabFM valuation, while turnkey listings earn actionable analyst briefs."
        ),
    },
    "tab8_chat": {
        "title": "Interactive Q&A — Ask Your Data (Grounded in the Open Knowledge Format)",
        "narrative": (
            "Use this conversational assistant during live customer Q&A to answer ad-hoc questions "
            "against the cotality_property dataset. Every natural-language prompt is grounded in the "
            "Open Knowledge Format semantic bundle and live table schemas so generated SQL automatically "
            "honors Cotality's governance rules (such as the 5% vacancy allowance and fixer-upper exclusion)."
        ),
        "takeaway": (
            "Empowers analysts and executives to explore live property valuations, metro forecasts, and "
            "photo insights in plain English while seeing the exact verified GoogleSQL executed."
        ),
        "qa_tip": (
            "Try asking: 'Which move-in-ready properties are priced below their TabFM comp valuation and "
            "what is their OKF effective rental yield?' or 'Compare 12-month forecasted price appreciation by metro.'"
        ),
    },
}

# ---------------------------------------------------------------------------
# Featured Properties Local Image Mapping (Matches Cotality_property_trend_demo.ipynb)
# ---------------------------------------------------------------------------
FEATURED_PROPERTY_PHOTOS: Dict[str, Dict[str, str]] = {
    "PROP-101": {
        "file": "prop_101_modern_custom_home.jpg",
        "caption": "PROP-101 · 418 Pine Ridge Trail, Denver, CO ($985k)",
    },
    "PROP-102": {
        "file": "prop_102_mediterranean_estate.jpg",
        "caption": "PROP-102 · 742 Palm Harbor Way, Miami, FL ($890k)",
    },
    "PROP-103": {
        "file": "prop_103_craftsman_bungalow.jpg",
        "caption": "PROP-103 · 964 Cedar Crest Ave, Seattle, WA ($825k)",
    },
    "PROP-104": {
        "file": "prop_104_austin_porch_cottage.jpg",
        "caption": "PROP-104 · 1170 San Bernard St, Austin, TX ($515k)",
    },
    "PROP-105": {
        "file": "prop_105_suburban_ranch_home.jpg",
        "caption": "PROP-105 · 215 Meadowbrook Ln, Phoenix, AZ ($465k)",
    },
    "PROP-106": {
        "file": "prop_106_distressed_fixer_upper.jpg",
        "caption": "PROP-106 · 809 Old Mill Rd, Austin, TX ($335k Fixer)",
    },
}


# ---------------------------------------------------------------------------
# Open Knowledge Format Semantic Bundle Builder (Matches Code Cell 10)
# ---------------------------------------------------------------------------
def ensure_knowledge_bundle(base_dir: Path, project_id: str, dataset_id: str) -> Dict[str, str]:
    """Creates or reads portable Open Knowledge Format Markdown + YAML files."""
    okf_dir = base_dir / "knowledge_bundle"
    for sub in ["datasets", "tables", "metrics", "computations"]:
        (okf_dir / sub).mkdir(parents=True, exist_ok=True)

    bq_ds_uri = f"//bigquery.googleapis.com/projects/{project_id}/datasets/{dataset_id}"
    files: Dict[str, str] = {
        "index.md": f"""---
title: "Cotality Residential Property & Comps Knowledge Bundle"
description: "Simplified Open Knowledge Format semantic layer covering properties, sold and rent history, comparable sales, and Effective Gross Rental Yield."
---

# Cotality Property & Comps — Open Knowledge Format

* [Datasets](datasets/) - Governed BigQuery dataset container (`{project_id}.{dataset_id}`).
* [Tables](tables/) - Core residential tables (`properties`, `sold_and_rent_history`, `property_comps`).
* [Metrics](metrics/) - Canonical Effective Gross Rental Yield (%) metric definition.
* [Computations](computations/) - Attested BigQuery SQL query for Effective Gross Rental Yield (%).
""",
        "tables/properties.md": f"""---
type: "BigQuery Table"
title: "Properties"
description: "Active residential properties with physical attributes, listing_notes, and Cloud Storage exterior photo URIs."
resource: "{bq_ds_uri}/tables/properties"
---

# Properties (`{project_id}.{dataset_id}.properties`)

One row per residential property (`property_id`, `address`, `metro_area`, `property_type`, `sqft`, `bedrooms`, `bathrooms`, `year_built`, `has_pool_or_view`, `list_price_usd`, `current_monthly_rent_usd`, `listing_notes`, `gcs_image_uri`).
""",
        "tables/sold_and_rent_history.md": f"""---
type: "BigQuery Table"
title: "Sold and Rent History"
description: "Monthly historical median_sold_price_usd and avg_monthly_rent_usd across 5 US metros."
resource: "{bq_ds_uri}/tables/sold_and_rent_history"
---

# Sold and Rent History (`{project_id}.{dataset_id}.sold_and_rent_history`)

Partitioned by `month_date` and clustered by `metro_area` (`month_date`, `metro_area`, `median_sold_price_usd`, `avg_monthly_rent_usd`, `homes_sold_count`) for zero-shot `AI.FORECAST` projections.
""",
        "tables/property_comps.md": f"""---
type: "BigQuery Table"
title: "Property Comps"
description: "Comparable sold and leased residential properties with sold_price_usd and monthly_rent_usd outcomes."
resource: "{bq_ds_uri}/tables/property_comps"
---

# Property Comps (`{project_id}.{dataset_id}.property_comps`)

Closed residential sales and leases (`comp_id`, `split_set`, `metro_area`, `property_type`, `sqft`, `bedrooms`, `bathrooms`, `year_built`, `has_pool_or_view`, `is_fixer_upper`, `sold_price_usd`, `monthly_rent_usd`) powering zero-shot `AI.PREDICT` valuation.
""",
        "metrics/effective_gross_rental_yield.md": f"""---
type: "Metric"
title: "Gross Rental Yield"
description: "Effective annualized rental yield (%) on move-in-ready residential homes after a 5% vacancy allowance."
resource: "{bq_ds_uri}/metrics/gross_rental_yield"
---

# Effective Gross Rental Yield (%)

* **Formula**: `ROUND(100.0 * SAFE_DIVIDE(SUM(12.0 * monthly_rent_usd * 0.95), SUM(sold_price_usd)), 2)`
* **Governance Rule**: Include only move-in-ready residential homes (`is_fixer_upper = FALSE`) and apply a `0.95` effective collection factor (`5%` annual vacancy allowance).
* **Attested SQL**: See [Gross Rental Yield SQL](../computations/effective_gross_rental_yield_sql.md).
""",
        "computations/effective_gross_rental_yield_sql.md": f"""---
type: "Attested Computation"
title: "Gross Rental Yield SQL"
description: "Verified BigQuery GoogleSQL query computing Effective Gross Rental Yield (%) by metro_area."
resource: "{bq_ds_uri}/computations/gross_rental_yield_sql"
runtime: "bigquery"
---

# Gross Rental Yield SQL

Implements [Gross Rental Yield](../metrics/effective_gross_rental_yield.md) across [Property Comps](../tables/property_comps.md).

```sql
SELECT
  metro_area,
  COUNT(*) AS move_in_ready_comps,
  ROUND(AVG(sold_price_usd), 0) AS avg_sold_price_usd,
  ROUND(AVG(monthly_rent_usd), 0) AS avg_monthly_rent_usd,
  ROUND(
    100.0 * SAFE_DIVIDE(SUM(12.0 * monthly_rent_usd * 0.95), SUM(sold_price_usd)),
    2
  ) AS effective_gross_rental_yield_pct
FROM `{project_id}.{dataset_id}.property_comps`
WHERE is_fixer_upper = FALSE
GROUP BY metro_area
ORDER BY effective_gross_rental_yield_pct DESC;
```
""",
    }

    for rel_path, content in files.items():
        target = okf_dir / rel_path
        target.write_text(content.strip() + "\n", encoding="utf-8")

    return files


# ---------------------------------------------------------------------------
# Step 2: DDL Builders for the 3 Core Tables (Matches Code Cell 8 Schema)
# ---------------------------------------------------------------------------
def get_create_core_tables_sql(project_id: str, dataset_id: str, bucket_name: str) -> Dict[str, str]:
    """Returns the 3 CREATE OR REPLACE TABLE statements matching Cotality_property_trend_demo.ipynb."""
    properties_sql = f"""CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.properties`
CLUSTER BY metro_area, property_type AS
WITH featured AS (
  SELECT 'PROP-101' AS property_id, '418 Pine Ridge Trail, Denver, CO' AS address, 'Denver, CO' AS metro_area,
    'Single-Family' AS property_type, 3450 AS sqft, 4 AS bedrooms, 3.5 AS bathrooms, 2019 AS year_built,
    TRUE AS has_pool_or_view, 985000.0 AS list_price_usd, 4950.0 AS current_monthly_rent_usd,
    'Custom contemporary stone-and-stucco foothills residence with woodland views, timber carport, chef kitchen, and turnkey finishes.' AS listing_notes,
    'gs://{bucket_name}/cotality_property_demo/images/prop_101_modern_custom_home.jpg' AS gcs_image_uri
  UNION ALL
  SELECT 'PROP-102', '742 Palm Harbor Way, Miami, FL', 'Miami, FL',
    'Single-Family', 3120, 4, 3.0, 2021, TRUE, 890000.0, 4800.0,
    'Upscale Mediterranean residence with barrel-tile roof, paver driveway, dual garage, resort patio, and impact windows in move-in-ready condition.',
    'gs://{bucket_name}/cotality_property_demo/images/prop_102_mediterranean_estate.jpg'
  UNION ALL
  SELECT 'PROP-103', '964 Cedar Crest Ave, Seattle, WA', 'Seattle, WA',
    'Single-Family', 2280, 3, 2.5, 1998, FALSE, 825000.0, 3950.0,
    'Well-maintained Craftsman single-family home featuring covered front porch with tapered columns, updated HVAC, and manicured landscaping.',
    'gs://{bucket_name}/cotality_property_demo/images/prop_103_craftsman_bungalow.jpg'
  UNION ALL
  SELECT 'PROP-104', '1170 San Bernard St, Austin, TX', 'Austin, TX',
    'Cottage', 1780, 3, 2.0, 1986, FALSE, 515000.0, 2720.0,
    'Charming East Austin clapboard cottage with wraparound front porch, updated shingle roof, bright living room, and cozy starter-home layout.',
    'gs://{bucket_name}/cotality_property_demo/images/prop_104_austin_porch_cottage.jpg'
  UNION ALL
  SELECT 'PROP-105', '215 Meadowbrook Ln, Phoenix, AZ', 'Phoenix, AZ',
    'Single-Family', 1960, 3, 2.0, 1996, FALSE, 465000.0, 2480.0,
    'Move-in-ready suburban single-story ranch home on spacious green lot with covered entry porch, updated kitchen appliances, and clean roof.',
    'gs://{bucket_name}/cotality_property_demo/images/prop_105_suburban_ranch_home.jpg'
  UNION ALL
  SELECT 'PROP-106', '809 Old Mill Rd, Austin, TX', 'Austin, TX',
    'Single-Family', 2050, 3, 1.5, 1962, FALSE, 335000.0, 1750.0,
    'Investor as-is fixer-upper needing full roof shingle replacement, exterior wood siding repaint, window glazing, and interior rehab.',
    'gs://{bucket_name}/cotality_property_demo/images/prop_106_distressed_fixer_upper.jpg'
),
synthetic AS (
  SELECT
    FORMAT('PROP-%d', idx) AS property_id,
    CONCAT(CAST(100 + idx * 3 AS STRING), ' Oak Dr, ',
      CASE MOD(idx, 5)
        WHEN 0 THEN 'Austin, TX'
        WHEN 1 THEN 'Miami, FL'
        WHEN 2 THEN 'Denver, CO'
        WHEN 3 THEN 'Phoenix, AZ'
        ELSE 'Seattle, WA'
      END
    ) AS address,
    CASE MOD(idx, 5)
      WHEN 0 THEN 'Austin, TX'
      WHEN 1 THEN 'Miami, FL'
      WHEN 2 THEN 'Denver, CO'
      WHEN 3 THEN 'Phoenix, AZ'
      ELSE 'Seattle, WA'
    END AS metro_area,
    CASE MOD(idx, 4)
      WHEN 2 THEN 'Townhome'
      ELSE 'Single-Family'
    END AS property_type,
    1400 + MOD(idx * 137, 2200) AS sqft,
    2 + MOD(idx, 4) AS bedrooms,
    CAST(1.5 + MOD(idx, 3) * 1.0 AS FLOAT64) AS bathrooms,
    1970 + MOD(idx * 19, 53) AS year_built,
    (MOD(idx, 4) = 1) AS has_pool_or_view,
    ROUND(480000.0 + (1400 + MOD(idx * 137, 2200)) * 145.0 - (CASE WHEN MOD(idx, 4) = 3 THEN 125000.0 ELSE 0.0 END), -2) AS list_price_usd,
    ROUND(2400.0 + (1400 + MOD(idx * 137, 2200)) * 0.65 - (CASE WHEN MOD(idx, 4) = 3 THEN 550.0 ELSE 0.0 END), -1) AS current_monthly_rent_usd,
    CASE MOD(idx, 4)
      WHEN 0 THEN 'Clean move-in-ready suburban family home with updated kitchen, solid roof, and fenced backyard.'
      WHEN 1 THEN 'Custom luxury residence featuring resort pool, scenic patio view, quartz counters, and designer finishes.'
      WHEN 2 THEN 'Cozy townhome ideal for first-time buyers with low-maintenance yard, fresh paint, and modern appliances.'
      ELSE 'Value-add fixer-upper sold as-is; requires roof repair, exterior siding work, and kitchen/bath renovation.'
    END AS listing_notes,
    CAST(NULL AS STRING) AS gcs_image_uri
  FROM UNNEST(GENERATE_ARRAY(107, 200)) AS idx
)
SELECT * FROM featured
UNION ALL
SELECT * FROM synthetic"""

    history_sql = f"""CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.sold_and_rent_history`
PARTITION BY DATE_TRUNC(month_date, MONTH)
CLUSTER BY metro_area AS
WITH metros AS (
  SELECT 'Austin, TX' AS metro_area, 515000.0 AS base_price, 2650.0 AS base_rent, 0.046 AS annual_growth UNION ALL
  SELECT 'Miami, FL',  640000.0, 3450.0, 0.058 UNION ALL
  SELECT 'Denver, CO', 590000.0, 2950.0, 0.042 UNION ALL
  SELECT 'Phoenix, AZ',455000.0, 2350.0, 0.044 UNION ALL
  SELECT 'Seattle, WA',760000.0, 3550.0, 0.049
),
months AS (
  SELECT
    month_date,
    DATE_DIFF(month_date, DATE '2020-01-01', MONTH) AS m_idx
  FROM UNNEST(GENERATE_DATE_ARRAY(DATE '2020-01-01', DATE '2025-12-01', INTERVAL 1 MONTH)) AS month_date
)
SELECT
  mo.month_date,
  m.metro_area,
  ROUND(
    m.base_price * 0.84 * POW(1.0 + m.annual_growth, mo.m_idx / 12.0)
    * (1.0 + 0.028 * SIN(2.0 * ACOS(-1.0) * (EXTRACT(MONTH FROM mo.month_date) - 3) / 12.0)),
    0
  ) AS median_sold_price_usd,
  ROUND(
    m.base_rent * 0.85 * POW(1.0 + m.annual_growth * 0.85, mo.m_idx / 12.0)
    * (1.0 + 0.018 * SIN(2.0 * ACOS(-1.0) * (EXTRACT(MONTH FROM mo.month_date) - 4) / 12.0)),
    0
  ) AS avg_monthly_rent_usd,
  CAST(ROUND(420.0 * (1.0 + 0.028 * SIN(2.0 * ACOS(-1.0) * (EXTRACT(MONTH FROM mo.month_date) - 3) / 12.0))) AS INT64) AS homes_sold_count
FROM metros m
CROSS JOIN months mo"""

    comps_sql = f"""CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.property_comps`
CLUSTER BY metro_area, property_type AS
WITH raw_comps AS (
  SELECT
    c_idx,
    FORMAT('COMP-%d', 1000 + c_idx) AS comp_id,
    CASE WHEN c_idx <= 190 THEN 'TRAIN' ELSE 'VALIDATION' END AS split_set,
    CASE MOD(c_idx, 5)
      WHEN 0 THEN 'Austin, TX'
      WHEN 1 THEN 'Miami, FL'
      WHEN 2 THEN 'Denver, CO'
      WHEN 3 THEN 'Phoenix, AZ'
      ELSE 'Seattle, WA'
    END AS metro_area,
    CASE
      WHEN MOD(c_idx, 5) < 3 THEN 'Single-Family'
      WHEN MOD(c_idx, 5) = 3 THEN 'Townhome'
      ELSE 'Cottage'
    END AS property_type,
    1200 + MOD(c_idx * 149, 2400) AS sqft,
    2 + MOD(c_idx, 4) AS bedrooms,
    CAST(1.5 + MOD(c_idx, 4) * 0.5 AS FLOAT64) AS bathrooms,
    CASE WHEN MOD(c_idx, 6) = 0 THEN 1962 + MOD(c_idx, 20) ELSE 1986 + MOD(c_idx, 37) END AS year_built,
    (MOD(c_idx, 6) != 0 AND MOD(c_idx, 4) = 0) AS has_pool_or_view,
    (MOD(c_idx, 6) = 0) AS is_fixer_upper
  FROM UNNEST(GENERATE_ARRAY(1, 240)) AS c_idx
)
SELECT
  comp_id,
  split_set,
  metro_area,
  property_type,
  sqft,
  bedrooms,
  bathrooms,
  year_built,
  has_pool_or_view,
  is_fixer_upper,
  ROUND(
    (CASE metro_area
      WHEN 'Austin, TX' THEN 515000.0
      WHEN 'Miami, FL'  THEN 640000.0
      WHEN 'Denver, CO' THEN 590000.0
      WHEN 'Phoenix, AZ' THEN 455000.0
      ELSE 760000.0
    END)
    * (CASE property_type WHEN 'Single-Family' THEN 1.00 WHEN 'Townhome' THEN 0.84 ELSE 0.78 END)
    * POW(sqft / 2100.0, 0.78)
    * (CASE WHEN has_pool_or_view THEN 1.12 ELSE 1.00 END)
    * (CASE WHEN is_fixer_upper THEN 0.68 ELSE 1.00 END),
    -2
  ) AS sold_price_usd,
  ROUND(
    (CASE metro_area
      WHEN 'Austin, TX' THEN 2650.0
      WHEN 'Miami, FL'  THEN 3450.0
      WHEN 'Denver, CO' THEN 2950.0
      WHEN 'Phoenix, AZ' THEN 2350.0
      ELSE 3550.0
    END)
    * (CASE property_type WHEN 'Single-Family' THEN 1.00 WHEN 'Townhome' THEN 0.84 ELSE 0.78 END)
    * POW(sqft / 2100.0, 0.62)
    * (CASE WHEN has_pool_or_view THEN 1.08 ELSE 1.00 END)
    * (CASE WHEN is_fixer_upper THEN 0.76 ELSE 1.00 END),
    -1
  ) AS monthly_rent_usd
FROM raw_comps"""

    return {
        "properties": properties_sql,
        "sold_and_rent_history": history_sql,
        "property_comps": comps_sql,
    }


# ---------------------------------------------------------------------------
# Step 4, 5, 6, 7, 8 Materialization & Live Execution Queries (Exact Notebook Match)
# ---------------------------------------------------------------------------
def get_step4_photo_insights_ddl(project_id: str, dataset_id: str, connection_id: str) -> str:
    make_ref_expr = (
        f"OBJ.MAKE_REF(p.gcs_image_uri, '{connection_id}')"
        if connection_id
        else "OBJ.MAKE_REF(p.gcs_image_uri)"
    )
    return f"""CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.property_photo_insights` AS
WITH refs AS (
  SELECT
    p.property_id,
    p.address,
    p.metro_area,
    p.list_price_usd,
    p.gcs_image_uri,
    OBJ.FETCH_METADATA({make_ref_expr}) AS image_ref
  FROM `{project_id}.{dataset_id}.properties` AS p
  WHERE p.gcs_image_uri IS NOT NULL
)
SELECT
  property_id,
  address,
  metro_area,
  list_price_usd,
  JSON_VALUE(image_ref.details, '$.gcs_metadata.content_type') AS content_type,
  ROUND(SAFE_CAST(JSON_VALUE(image_ref.details, '$.gcs_metadata.size') AS INT64) / 1024.0, 1) AS image_kb,
  (AI.GENERATE(
    (
      'You are a residential property appraiser. Inspect this exterior house photograph and extract the architectural style, exterior condition (Excellent, Good, Fair, or Poor - Needs Rehab), a curb appeal score from 1 (severely distressed) to 10 (luxury showcase), key visible exterior features, and a concise 1-sentence visual summary.',
      image_ref
    ),
    output_schema => 'architectural_style STRING, exterior_condition STRING, curb_appeal_score INT64, visible_features ARRAY<STRING>, photo_summary STRING'
  )).*
FROM refs
ORDER BY property_id"""


def get_step5_screening_ddl(project_id: str, dataset_id: str, connection_id: str, sample_limit: int = 25) -> str:
    del connection_id
    return f"""CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.properties_enriched` AS
WITH sample_props AS (
  SELECT *
  FROM `{project_id}.{dataset_id}.properties`
  ORDER BY gcs_image_uri IS NULL ASC, property_id ASC
  LIMIT {sample_limit}
)
SELECT
  p.property_id,
  p.address,
  p.metro_area,
  p.property_type,
  p.sqft,
  p.bedrooms,
  p.bathrooms,
  p.year_built,
  p.has_pool_or_view,
  p.list_price_usd,
  p.current_monthly_rent_usd,
  p.listing_notes,
  p.gcs_image_uri,
  AI.IF(
    (
      'Is this residential property move-in ready without needing major roof, siding, structural, or as-is renovation repairs? Listing: ',
      p.listing_notes
    ),
    examples => [
      ('Updated 4-bedroom suburban home with solid roof, modern kitchen, and fenced yard.', TRUE),
      ('As-is investor fixer-upper needing roof replacement, siding repair, and interior rehab.', FALSE)
    ]
  ) AS is_move_in_ready,
  AI.CLASSIFY(
    p.listing_notes,
    categories => [
      ('Turnkey Family Home', 'Move-in-ready 3+ bedroom suburban family residence in good condition'),
      ('Luxury Residence', 'Upscale custom home with pool, scenic view, or luxury architectural finishes'),
      ('Fixer-Upper / Value-Add', 'Older or distressed as-is property requiring roof, siding, or interior renovation'),
      ('Starter / Cozy Home', 'Compact townhome or cottage suited for entry-level or cozy low-maintenance living')
    ]
  ) AS buyer_segment
FROM sample_props AS p"""


def get_step6_backtest_sql(project_id: str, dataset_id: str) -> str:
    return f"""SELECT
  metro_area,
  'Median Sold Price (USD)' AS metric_name,
  ROUND(mean_absolute_percentage_error, 2) AS mape_pct,
  ROUND(mean_absolute_error, 0) AS mae_usd
FROM AI.EVALUATE(
  (SELECT month_date, metro_area, median_sold_price_usd
   FROM `{project_id}.{dataset_id}.sold_and_rent_history`
   WHERE month_date < DATE '2025-01-01'),
  (SELECT month_date, metro_area, median_sold_price_usd
   FROM `{project_id}.{dataset_id}.sold_and_rent_history`
   WHERE month_date >= DATE '2025-01-01'),
  data_col => 'median_sold_price_usd',
  timestamp_col => 'month_date',
  id_cols => ['metro_area'],
  horizon => 12
)
UNION ALL
SELECT
  metro_area,
  'Avg Monthly Rent (USD)' AS metric_name,
  ROUND(mean_absolute_percentage_error, 2) AS mape_pct,
  ROUND(mean_absolute_error, 1) AS mae_usd
FROM AI.EVALUATE(
  (SELECT month_date, metro_area, avg_monthly_rent_usd
   FROM `{project_id}.{dataset_id}.sold_and_rent_history`
   WHERE month_date < DATE '2025-01-01'),
  (SELECT month_date, metro_area, avg_monthly_rent_usd
   FROM `{project_id}.{dataset_id}.sold_and_rent_history`
   WHERE month_date >= DATE '2025-01-01'),
  data_col => 'avg_monthly_rent_usd',
  timestamp_col => 'month_date',
  id_cols => ['metro_area'],
  horizon => 12
)
ORDER BY metric_name, mape_pct ASC"""


def get_step6_forecast_ddl(project_id: str, dataset_id: str) -> str:
    return f"""CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.metro_12m_forecasts` AS
WITH sold_fc AS (
  SELECT
    metro_area,
    DATE(time_series_timestamp) AS month_date,
    IF(time_series_type = 'history', time_series_data, NULL) AS hist_sold_price_usd,
    IF(time_series_type = 'forecast', time_series_data, NULL) AS fc_sold_price_usd,
    prediction_interval_lower_bound AS sold_lower_usd,
    prediction_interval_upper_bound AS sold_upper_usd
  FROM AI.FORECAST(
    TABLE `{project_id}.{dataset_id}.sold_and_rent_history`,
    data_col => 'median_sold_price_usd',
    timestamp_col => 'month_date',
    id_cols => ['metro_area'],
    horizon => 12,
    confidence_level => 0.95,
    output_historical_time_series => TRUE
  )
),
rent_fc AS (
  SELECT
    metro_area,
    DATE(time_series_timestamp) AS month_date,
    IF(time_series_type = 'history', time_series_data, NULL) AS hist_rent_usd,
    IF(time_series_type = 'forecast', time_series_data, NULL) AS fc_rent_usd,
    prediction_interval_lower_bound AS rent_lower_usd,
    prediction_interval_upper_bound AS rent_upper_usd
  FROM AI.FORECAST(
    TABLE `{project_id}.{dataset_id}.sold_and_rent_history`,
    data_col => 'avg_monthly_rent_usd',
    timestamp_col => 'month_date',
    id_cols => ['metro_area'],
    horizon => 12,
    confidence_level => 0.95,
    output_historical_time_series => TRUE
  )
)
SELECT
  s.metro_area,
  s.month_date,
  MAX(s.hist_sold_price_usd) AS hist_sold_price_usd,
  MAX(s.fc_sold_price_usd) AS fc_sold_price_usd,
  MAX(s.sold_lower_usd) AS sold_lower_usd,
  MAX(s.sold_upper_usd) AS sold_upper_usd,
  MAX(r.hist_rent_usd) AS hist_rent_usd,
  MAX(r.fc_rent_usd) AS fc_rent_usd,
  MAX(r.rent_lower_usd) AS rent_lower_usd,
  MAX(r.rent_upper_usd) AS rent_upper_usd
FROM sold_fc AS s
JOIN rent_fc AS r
  USING (metro_area, month_date)
GROUP BY metro_area, month_date
ORDER BY metro_area, month_date"""


def get_step7_eval_sql(project_id: str, dataset_id: str) -> str:
    return f"""SELECT
  'sold_price_usd' AS target_column,
  ROUND(mean_absolute_error, 0) AS mae_usd,
  ROUND(mean_squared_error, 0) AS mse_usd,
  ROUND(r2_score, 4) AS r2_score
FROM AI.EVALUATE(
  (SELECT metro_area, property_type, sqft, bedrooms, bathrooms, year_built, has_pool_or_view, is_fixer_upper, sold_price_usd
   FROM `{project_id}.{dataset_id}.property_comps` WHERE split_set = 'TRAIN'),
  (SELECT metro_area, property_type, sqft, bedrooms, bathrooms, year_built, has_pool_or_view, is_fixer_upper, sold_price_usd
   FROM `{project_id}.{dataset_id}.property_comps` WHERE split_set = 'VALIDATION'),
  label_col => 'sold_price_usd'
)
UNION ALL
SELECT
  'monthly_rent_usd' AS target_column,
  ROUND(mean_absolute_error, 0) AS mae_usd,
  ROUND(mean_squared_error, 0) AS mse_usd,
  ROUND(r2_score, 4) AS r2_score
FROM AI.EVALUATE(
  (SELECT metro_area, property_type, sqft, bedrooms, bathrooms, year_built, has_pool_or_view, is_fixer_upper, monthly_rent_usd
   FROM `{project_id}.{dataset_id}.property_comps` WHERE split_set = 'TRAIN'),
  (SELECT metro_area, property_type, sqft, bedrooms, bathrooms, year_built, has_pool_or_view, is_fixer_upper, monthly_rent_usd
   FROM `{project_id}.{dataset_id}.property_comps` WHERE split_set = 'VALIDATION'),
  label_col => 'monthly_rent_usd'
)"""


def get_step7_predict_ddl(project_id: str, dataset_id: str) -> str:
    return f"""CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.property_comp_valuations` AS
WITH sold_preds AS (
  SELECT
    property_id,
    address,
    metro_area,
    property_type,
    sqft,
    bedrooms,
    bathrooms,
    year_built,
    is_move_in_ready,
    buyer_segment,
    list_price_usd,
    current_monthly_rent_usd,
    ROUND(predicted_sold_price_usd, 0) AS comp_predicted_sold_usd
  FROM AI.PREDICT(
    (SELECT metro_area, property_type, sqft, bedrooms, bathrooms, year_built, has_pool_or_view, is_fixer_upper, sold_price_usd
     FROM `{project_id}.{dataset_id}.property_comps` WHERE split_set = 'TRAIN'),
    (SELECT
       property_id, address, metro_area, property_type, sqft, bedrooms, bathrooms, year_built, has_pool_or_view,
       NOT is_move_in_ready AS is_fixer_upper,
       is_move_in_ready, buyer_segment, list_price_usd, current_monthly_rent_usd
     FROM `{project_id}.{dataset_id}.properties_enriched`),
    label_col => 'sold_price_usd'
  )
),
rent_preds AS (
  SELECT
    property_id,
    ROUND(predicted_monthly_rent_usd, 0) AS comp_predicted_rent_usd
  FROM AI.PREDICT(
    (SELECT metro_area, property_type, sqft, bedrooms, bathrooms, year_built, has_pool_or_view, is_fixer_upper, monthly_rent_usd
     FROM `{project_id}.{dataset_id}.property_comps` WHERE split_set = 'TRAIN'),
    (SELECT
       property_id, metro_area, property_type, sqft, bedrooms, bathrooms, year_built, has_pool_or_view,
       NOT is_move_in_ready AS is_fixer_upper
     FROM `{project_id}.{dataset_id}.properties_enriched`),
    label_col => 'monthly_rent_usd'
  )
)
SELECT
  s.*,
  r.comp_predicted_rent_usd,
  ROUND(s.comp_predicted_sold_usd - s.list_price_usd, 0) AS estimated_equity_spread_usd,
  ROUND(100.0 * SAFE_DIVIDE(12.0 * r.comp_predicted_rent_usd * 0.95, s.comp_predicted_sold_usd), 2) AS okf_effective_yield_pct
FROM sold_preds AS s
JOIN rent_preds AS r USING (property_id)
ORDER BY property_id"""


def get_step8_unified_cards_sql(project_id: str, dataset_id: str, connection_id: str) -> str:
    del connection_id
    return f"""WITH metro_growth AS (
  SELECT
    h.metro_area,
    ROUND(100.0 * (f.fc_sold_price_usd - h.median_sold_price_usd) / h.median_sold_price_usd, 1) AS metro_12m_price_growth_pct,
    ROUND(100.0 * (f.fc_rent_usd - h.avg_monthly_rent_usd) / h.avg_monthly_rent_usd, 1) AS metro_12m_rent_growth_pct
  FROM `{project_id}.{dataset_id}.sold_and_rent_history` AS h
  JOIN `{project_id}.{dataset_id}.metro_12m_forecasts` AS f
    ON h.metro_area = f.metro_area AND f.month_date = DATE '2026-12-01'
  WHERE h.month_date = DATE '2025-12-01'
)
SELECT
  v.property_id,
  v.address,
  v.metro_area,
  v.buyer_segment,
  v.is_move_in_ready,
  img.architectural_style,
  img.exterior_condition,
  img.curb_appeal_score,
  img.photo_summary,
  v.list_price_usd,
  v.comp_predicted_sold_usd,
  v.estimated_equity_spread_usd,
  v.comp_predicted_rent_usd,
  v.okf_effective_yield_pct,
  g.metro_12m_price_growth_pct,
  g.metro_12m_rent_growth_pct,
  (AI.GENERATE(
    CONCAT(
      'Write a crisp 2-sentence residential valuation brief for a property analyst. ',
      'Property ', v.property_id, ' (', v.address, ') is classified as ', v.buyer_segment,
      ' with exterior photo condition "', img.exterior_condition, '" (curb appeal ', CAST(img.curb_appeal_score AS STRING), '/10: ', img.photo_summary, '). ',
      'List price is $', CAST(CAST(v.list_price_usd AS INT64) AS STRING),
      ' vs AI.PREDICT comp value $', CAST(CAST(v.comp_predicted_sold_usd AS INT64) AS STRING),
      ' and predicted rent $', CAST(CAST(v.comp_predicted_rent_usd AS INT64) AS STRING), '/mo ',
      '(OKF Effective Gross Rental Yield: ', CAST(v.okf_effective_yield_pct AS STRING), '%), ',
      'with metro 12-month price growth forecast at ', CAST(g.metro_12m_price_growth_pct AS STRING), '%.'
    ),
    output_schema => 'recommendation_tag STRING, analyst_valuation_brief STRING'
  )).*
FROM `{project_id}.{dataset_id}.property_comp_valuations` AS v
JOIN `{project_id}.{dataset_id}.property_photo_insights` AS img USING (property_id)
JOIN metro_growth AS g ON v.metro_area = g.metro_area
ORDER BY v.property_id"""
