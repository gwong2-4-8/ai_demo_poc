<!--
Copyright 2026 Google LLC
SPDX-License-Identifier: Apache-2.0
-->

# Cotality Property Trend & AI Valuation — Cloud Run WebApp

An interactive **Google Cloud Run** web application built with **Streamlit**, **Plotly**, and the **Google Cloud BigQuery & Storage SDKs** to demonstrate end-to-end **Generative AI, Multimodal Object Tables, Time-Series Forecasting (`TimesFM`), and Zero-Shot Tabular Valuation (`TabFM`)** directly inside BigQuery SQL.

Every demo stage includes a toggleable **🎙️ Presenter Talk Track & Value Takeaway** panel drawn from `Cotality_property_trend_demo_talk_track.md`, transparent GoogleSQL inspection, and live query execution telemetry against `<PROJECT_ID>.<DATASET_ID>`.

---

## Demo Stages & Capabilities

1. **Tab 1 — Architecture & Data Foundation**: Displays the 16:9 Google Cloud architecture diagram, live table status & partitioning/clustering metadata (`properties`, `sold_and_rent_history`, `property_comps`), automated `ML.DESCRIBE_DATA` profiling, and a 1-click **Provision / Refresh Demo Tables & GCS Photos** action.
2. **Tab 2 — Open Knowledge Format Grounding**: Side-by-side execution comparing **Ungrounded Schema-Only `AI.GENERATE`** against **Open Knowledge Format Grounded `AI.GENERATE`** for *Effective Gross Rental Yield (%)* (`5%` vacancy haircut, excluding fixer-uppers, portfolio-weighted `SAFE_DIVIDE`).
3. **Tab 3 — Multimodal Photo Inspection (`ObjectRef` + `AI.GENERATE`)**: Visual gallery of the 6 CC0 residential exterior photos (`PROP-101` to `PROP-106`) paired with structured fields extracted by Gemini directly inside SQL (`architectural_style`, `exterior_condition`, `curb_appeal_score`, `visible_features`, `photo_summary`).
4. **Tab 4 — Listing Screening & Buyer Segmentation (`AI.IF` + `AI.CLASSIFY`)**: Semantic boolean screening (`is_move_in_ready`) and zero-shot classification (`Turnkey Family Home`, `Luxury Residence`, `Fixer-Upper / Value-Add`, `Starter / Cozy Home`), plus an interactive **Live Ad-Hoc Listing Screener**.
5. **Tab 5 — 12-Month Metro Price & Rent Forecast (`TimesFM`)**: Zero-training multi-series forecasting (`id_cols => ['metro_area']`) with 2025 holdout backtest (`AI.EVALUATE` MAPE/MAE) and interactive 2-panel Plotly fan charts (`95%` confidence intervals).
6. **Tab 6 — Zero-Shot Comparable Valuation (`TabFM`)**: In-context tabular regression (`AI.PREDICT` + `AI.EVALUATE`) chaining Step 5 `AI.IF` (`NOT is_move_in_ready AS is_fixer_upper`) to predict fair-value sold price and monthly rent across active listings.
7. **Tab 7 — Unified Property Valuation Cards**: Joins `TabFM` comp valuations, `TimesFM` 12-month metro appreciation trajectories, and multimodal photo condition into a 2-sentence `AI.GENERATE` executive valuation brief (`BUY` / `HOLD` / `PASS`).
8. **Tab 8 — Ask Your Data (Gemini Natural-Language SQL Assistant)**: Interactive natural-language Q&A grounded in the Open Knowledge Format semantic bundle that generates, executes, and explains BigQuery GoogleSQL queries on the fly.

---

## Running Locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

export PROJECT_ID="cotality-proj"
export DATASET_ID="cotality_property"
export LOCATION="US"
export BUCKET_NAME="cotality-workshop"
export CONNECTION_ID="us.cotality-conn"

.venv/bin/streamlit run app.py --server.port 8080
```

---

## Deploying to Google Cloud Run

```bash
chmod +x deploy.sh
./deploy.sh
```

Ensure the Cloud Run runtime service account has:
* `roles/bigquery.user` and `roles/bigquery.dataEditor` on `PROJECT_ID`
* `roles/bigquery.connectionUser` on the Cloud Resource connection (`CONNECTION_ID`)
* `roles/storage.objectAdmin` (or `objectViewer` if pre-staged) on `gs://${BUCKET_NAME}`
