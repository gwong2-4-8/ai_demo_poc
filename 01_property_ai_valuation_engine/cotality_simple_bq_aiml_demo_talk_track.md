# Presenter Talk Track Guide: `Cotality_property_trend_demo.ipynb`

> **Document Scope**: Live workshop presenter script, timing guide, and Q&A cheat sheet accompanying `Cotality_property_trend_demo.ipynb` (and `cotality_simple_property_aiml_lab.ipynb`), `./property_images/`, `gs://<BUCKET>/property_okf/`, and the slide-ready architecture diagram [cotality_property_trend_demo_architecture.png](file:///usr/local/google/home/cannis/ace/cotality/cotality_property_trend_demo_architecture.png) ([Cotality_property_trend_demo_architecture.md](file:///usr/local/google/home/cannis/ace/cotality/Cotality_property_trend_demo_architecture.md)) (`Copyright 2026 Google LLC`, `SPDX-License-Identifier: Apache-2.0`).

---

## 1. End-to-End Demo Structure (~15–18 Minutes)

This notebook runs **top-to-bottom in a single click (`Run All`)** using **3 core BigQuery tables** and **6 real residential exterior photographs** (CC0 / Public Domain), and **automatically cleans up** the created BigQuery dataset, Cloud Storage demo photos, and `property_okf/` bundle in Step 9:

1. **`properties`** (`100` active homes — physical attributes, `list_price_usd`, `listing_notes`, and `gcs_image_uri` pointers to 6 real Cloud Storage house photos).
2. **`sold_and_rent_history`** (`360` monthly rows = `5` US metros × `72` months of `median_sold_price_usd` and `avg_monthly_rent_usd`).
3. **`property_comps`** (`240` closed comparable sales and leases with verified `sold_price_usd` and `monthly_rent_usd` outcomes).
4. **`(Optional) gs://<BUCKET>/property_okf/`**: Open Knowledge Format (`OKF v0.2`) semantic bundle (`RUN_OPTIONAL_OKF = True` by default; uncheck to skip Step 3 cleanly during shorter demos).

---

## 2. Pre-Demo Checklist (60 Seconds Before Going Live)

1. Open `Cotality_property_trend_demo.ipynb` in **BigQuery Studio (Colab Enterprise)** or **Vertex AI Workbench**.
2. Confirm **Step 1.2** parameters match your workshop project (`PROJECT_ID = "cotality-proj"`, `DATASET_ID = "cotality_property"`, `BUCKET_NAME = "cotality-workshop"`, `CONNECTION_ID = "us.cotality-conn"`).
3. Decide your timing & cleanup toggles:
   * **Short 12-Minute Track**: Uncheck `RUN_OPTIONAL_OKF` in Step 3.1 (skips Step 3.1 & Step 3.2 in `<0.01s`; Steps 4–9 have zero dependency on Step 3).
   * **Full 18-Minute Track**: Keep `RUN_OPTIONAL_OKF = True` (uploads all 12 OKF files to `gs://cotality-workshop/property_okf/` and grounds `AI.GENERATE` directly from Cloud Storage).
   * **Keep Tables Alive During Q&A?**: `RUN_CLEANUP = True` in Step 9 cleans up automatically at the end of `Run All`. If you want to run ad-hoc SQL during Q&A before cleaning up, uncheck `RUN_CLEANUP` first and run Step 9 at the end of Q&A.

---

## 3. Cell-by-Cell Live Presenter Talk Track

### Opening & Step 1 — Setup & Governed IAM Connection (~2 min)
* **On Screen**: Architecture overview table (Cell 0) + Step 1.2 parameter form (Cell 4).
* **Talk Track**:
  > *"In this live demo, we're keeping the data model super simple—just the three tables every property analytics team knows by heart: active **Properties**, monthly **Sold & Rent History**, and closed **Property Comps**, plus **real exterior house photos** in Cloud Storage. Notice our Cloud Resource Connection (`us.cotality-conn`), which lets BigQuery access Cloud Storage photos and Vertex AI foundation models under governed IAM delegation—while leaving `CONNECTION_ID` blank falls back to end-user credentials in personal sandboxes."*

### Step 2 — Real Property Photos & 3 Core BigQuery Tables (~2.5 min)
* **On Screen**: The 2×3 gallery of the **6 real residential photographs** (`PROP-101` `$985k` contemporary stone residence, `PROP-102` `$890k` Mediterranean barrel-tile home, `PROP-103` `$825k` Craftsman bungalow, `PROP-104` `$515k` Austin wraparound-porch cottage, `PROP-105` `$465k` suburban ranch, and `PROP-106` `$335k` distressed fixer-upper) + `ML.DESCRIBE_DATA` summary.
* **Talk Track**:
  > *"Look at the 6 real house photos staged in `gs://cotality-workshop/cotality_property_demo/images/`. Compare `PROP-101` and `PROP-102` against `PROP-106`, which has peeling clapboard siding and deteriorated roof shingles. Structured bedroom/bathroom columns alone can't capture visual condition—Gemini will extract it directly from these `.jpg` files in Step 4. Below that, we create our 3 partitioned and clustered BigQuery tables and sanity-check `property_comps` in one statement with `ML.DESCRIBE_DATA`."*

### (Optional) Step 3 — Open Knowledge Format (`OKF v0.2`) in `gs://<BUCKET>/property_okf/` (~2.5 min)
* **On Screen**: Step 3.1 upload confirmation (`Validated & uploaded 12 OKF v0.2 files to gs://cotality-workshop/property_okf/`) + Step 3.2 side-by-side `AI.GENERATE` output.
* **Talk Track**:
  > *"Even on a 3-table schema, ask two analysts for **Effective Gross Rental Yield (%)** and you'll get two different formulas unless the business rule is governed. Here we package our table schemas and KPI rule—excluding fixer-uppers (`is_fixer_upper = FALSE`) and applying a `5%` vacancy allowance (`0.95` collection factor)—in Open Knowledge Format (`OKF v0.2`) and store it centrally at `gs://cotality-workshop/property_okf/`. In Step 3.2, ungrounded `AI.GENERATE` guesses a naive `12 * rent / price` across distressed homes, whereas grounding directly from `gs://cotality-workshop/property_okf/` produces our exact attested BigQuery SQL."*

### Step 4 — Visual Photo Inspection (`OBJ.MAKE_REF` + Multimodal `AI.GENERATE`) (~3 min)
* **On Screen**: `property_photo_insights` DataFrame + annotated 2×3 photo grid showing Gemini's `curb_appeal_score` (`1–10`) and `exterior_condition` above each house.
* **Talk Track**:
  > *"Here is `ObjectRef` in action. `OBJ.MAKE_REF` creates a lightweight, IAM-governed pointer to each `.jpg` in Cloud Storage, and `OBJ.FETCH_METADATA` populates file size (`image_kb`) and MIME type—no public signed URLs, no base64 blobs, and full VPC Service Controls support. Passing `image_ref` into `AI.GENERATE` with `output_schema` returns typed BigQuery columns (`curb_appeal_score INT64`, `exterior_condition STRING`), scoring our turnkey residences `8–9/10` and flagging `PROP-106` at `1–2/10 (Poor - Needs Rehab)`."*

### Step 5 — Semantic Listing Screening (`AI.IF`) & Buyer Segmentation (`AI.CLASSIFY`) (~2 min)
* **On Screen**: `properties_enriched` table (`14s` runtime for 25 homes) + stacked horizontal bar chart.
* **Talk Track**:
  > *"Next, we enrich free-text `listing_notes` without brittle `REGEXP_CONTAINS` rules or JSON parsing. `AI.IF` returns a native SQL `BOOL` (`is_move_in_ready`), and `AI.CLASSIFY` assigns each home into one of four governed buyer segments (`Turnkey Family Home`, `Luxury Residence`, `Fixer-Upper / Value-Add`, `Starter / Cozy Home`). Even better, we pass `NOT is_move_in_ready` straight into `AI.PREDICT` in Step 7!"*

### Step 6 — Metro Sold Price & Rent Forecasting (`AI.FORECAST` — TimesFM) (~2.5 min)
* **On Screen**: `AI.EVALUATE` holdout MAPE table (~`1.4%`–`2%` MAPE in `1.5s`) + `AI.FORECAST` (`4.8s`) two-panel Austin, TX **Sold Price** and **Monthly Rent** fan charts.
* **Talk Track**:
  > *"Now let's forecast market trends from `sold_and_rent_history`. First, `AI.EVALUATE` backtests **TimesFM** on our 2025 holdout window (~`1.4%` MAPE). Then one SQL query calls `AI.FORECAST` with `id_cols => ['metro_area']` and `output_historical_time_series => TRUE` to forecast 12 months of both sold prices and monthly rents with 95% confidence bands in under 5 seconds—zero per-metro ARIMA training required."*

### Step 7 — Zero-Shot Comp Valuation (`AI.PREDICT` — TabFM, *Public Preview*) (~2.5 min)
* **On Screen**: `AI.EVALUATE` validation metrics (`mae_usd`, `mse_usd`, `r2_score` in `2.2s`) + scatter plot of **Asking List Price vs. `AI.PREDICT` Comp Value** (~`60s` execution for dual sold + rent predictions).
* **60-Second Pacing Talk Track (deliver while Cell 20 runs)**:
  > *"Look at `AI.EVALUATE` first—**TabFM** validates against our 50 held-out comps in ~2 seconds with strong $R^2$ accuracy. Now, while this second query runs (~60 seconds because it executes **two** zero-shot TabFM passes—one predicting `sold_price_usd` and a second predicting `monthly_rent_usd`), look at what is **not** in our SQL: there is **no `CREATE MODEL` statement**, no feature preprocessing pipeline, and no serving endpoint to maintain. `AI.PREDICT` uses our 190 closed `TRAIN` comps as in-context tabular examples, and feeds `NOT is_move_in_ready AS is_fixer_upper` from `AI.IF` so `PROP-106` is automatically priced against fixer-upper comps!"*

### Step 8 & Step 9 — Unified Valuation Cards (`AI.GENERATE`) & Automated Cleanup (~2 min)
* **On Screen**: The 6 `🏠 PROP-101..106` valuation briefs (`5.2s` runtime) + Step 9 cleanup confirmation.
* **Talk Track**:
  > *"Finally, one standard SQL `JOIN` brings together photo curb appeal, buyer segment, 12-month metro appreciation, and zero-shot comp valuation into a concise 2-sentence brief per property. And in Step 9 (`RUN_CLEANUP = True`), the notebook automatically deletes our demo BigQuery dataset (`cotality_property`), staged images (`cotality_property_demo/`), and `property_okf/` objects while keeping the shared `cotality-workshop` bucket intact—so the entire demo is 100% repeatable end-to-end."*

---

## 4. Workshop Q&A Cheat Sheet

| Question | Crisp Technical Answer |
| :--- | :--- |
| **How does `OBJ.MAKE_REF` handle security and VPC-SC?** | `OBJ.MAKE_REF(uri, connection_id)` creates an `ObjectRef` struct inside BigQuery. Access is governed by IAM (via Cloud Resource Connection or end-user credentials) and works inside VPC Service Controls perimeters without exposing public or signed URLs. |
| **When should we use `AI.PREDICT` vs. `CREATE MODEL` (`BOOSTED_TREE_REGRESSOR`)?** | Use `AI.PREDICT` (*Public Preview*, **TabFM**) for rapid zero-shot baselines, localized comp sets (up to 32k context rows), and ad-hoc SQL exploration without training pipelines. Use `CREATE MODEL` when scoring millions of parcels on a strict latency SLA or requiring persisted model registry artifacts. |
| **When should we use `AI.FORECAST` vs. `ARIMA_PLUS`?** | `AI.FORECAST` (**TimesFM**) requires zero model fitting—ideal for instant multi-series forecasting across metros or ZIP codes. Use `ARIMA_PLUS` / `ARIMA_PLUS_XREG` when you need explicit holiday effects, anomaly decomposition, or persisted model objects. |
| **Why store `property_okf/` in Cloud Storage?** | Storing Open Knowledge Format (`OKF v0.2`) Markdown + YAML files in `gs://<BUCKET>/property_okf/` gives notebooks, scheduled SQL jobs, and BigQuery Knowledge Catalog workflows one shared, versioned source of truth for KPI definitions and exclusions. |
