# Presenter Demo Guide & Talk Tracks: Cotality Property Portfolio Intelligence in BigQuery

**Companion Notebook:** `cotality_property_aiml_lab.ipynb`  
**Knowledge Bundle:** `cotality_property_okf/` (Open Knowledge Format v0.2)  
**Target Audience:** Cotality Data Architecture, Property Analytics, Valuation Science & Engineering Leaders  

---

## 1. Demo Pacing Options

| Format | Total Duration | Recommended Walkthrough Flow |
| :--- | :--- | :--- |
| **Full Technical Workshop** | **25–30 min** | Run **Steps 1 → 8** live end-to-end; pause on SQL blocks in Steps 3, 4, 5, 6, and 7 to inspect syntax and visual charts. |
| **Executive Fast-Track** | **12 min** | Pre-run Steps 1–2 before screen share; start at the **2×3 Property Image Grid (Step 2.1)** $\rightarrow$ **OKF Context Ceiling (Step 3.2)** $\rightarrow$ **Multimodal Roof Underwriting (Step 4)** $\rightarrow$ **TabFM Zero-Shot Rent Valuation (Step 7)** $\rightarrow$ **Executive Action Synthesis (Step 8)**. |

---

## 2. Step-by-Step Spoken Talk Tracks & On-Screen Cues

### Opening Hook (Overview Table — 1 min)
* **On-Screen Cue:** Scroll to the **Overview** table at the top of `cotality_property_aiml_lab.ipynb`.
* **Talk Track:**
  > *"Property intelligence workflows usually force data teams to maintain five separate stacks: Cloud Storage plus Python vision containers for roof inspection imagery, an NLP service for resident maintenance tickets, a BI wiki for KPI formulas, a forecasting pipeline for market rent outlooks, and custom feature-engineering jobs for automated valuation. In the next 20 minutes, we're going to execute all five workflows **in place inside BigQuery using standard GoogleSQL**—governed by an Open Knowledge Format semantic bundle so every AI output respects Cotality's underwriting guardrails."*

---

### Step 1: Zero-Friction Setup & End-User Multimodal Auth (2 min)
* **On-Screen Cue:** Highlight `CONNECTION_ID = ""` and the `Direct End-User Credentials` line in the Step 1.1 status banner.
* **Talk Track:**
  > *"Notice what we did **not** have to set up before writing AI SQL: we didn't provision GPU clusters, deploy model endpoints, or wait on service-account IAM propagation. BigQuery's generative and foundation-model functions execute server-side and support **end-user credentials** directly—so any analyst with Vertex AI User and Storage Viewer access can prototype immediately, while scheduled production pipelines can pass an optional Cloud Resource Connection ID."*

---

### Step 2: Sample Property Tables & Unstructured Inspection Photos (3 min)
* **On-Screen Cue:**
  1. Show the **2×3 inspection image grid** (`PROP-1001` intact roof, `PROP-1002` Denver hail shingle loss, `PROP-1003` Tampa ceiling drywall leak, `PROP-1004` Phoenix solar roof, `PROP-1005` Seattle stucco crack & gutter overflow, `PROP-1006` Miami elevated coastal residence).
  2. Point out `PARTITION BY` and `CLUSTER BY` in the DDL plus the `ML.DESCRIBE_DATA` profile table.
* **Talk Track:**
  > *"Here we materialize four realistic property tables—180 managed parcels, unstructured maintenance tickets, 84 months of metro rent history, and 360 comparable leases—using date partitioning and multi-column clustering on `metro_area`, `property_type`, and `risk_zone`. Alongside the structured tables, we upload six field-inspection images to Cloud Storage. Historically, structured parcel rows and unstructured inspection PNGs lived in two different worlds; next, we'll unify them."*

---

### Step 3: Open Knowledge Format (OKF v0.2) — Breaking the "Context Ceiling" (4 min)
* **On-Screen Cue:** Show the generated 15+ Markdown files under `cotality_property_okf/` (`datasets/`, `tables/`, `metrics/`, `computations/`, `policies/`) and compare **`1. Ungrounded (Raw Column Names Only)`** vs. **`2. OKF v0.2 Grounded`** in Step 3.2.
* **Talk Track:**
  > *"Why do enterprise text-to-SQL and AI analytics projects stall in production? They hit the **Context Ceiling**. Look at Step 3.2: if an LLM only sees column names like `current_monthly_rent_usd` and `estimated_asset_value_usd`, it writes `12 * rent / asset_value`—overstating yield on vacant turnovers and hail-damaged roofs! With **Open Knowledge Format (OKF v0.2)**—an open, Git-friendly Markdown + YAML standard integrated with Google Cloud Knowledge Catalog—we codify our table contracts, attested SQL computations, and underwriting policies (`exclude Vacant-Turn`, `0.96` occupancy allowance, deduct hazard capex reserves, `0%` rent freeze on damaged homes). Once grounded in OKF, BigQuery applies the exact institutional formula."*

---

### Step 4: Multimodal Property & Roof Inspection (`OBJ.MAKE_REF` + `AI.GENERATE`) (4 min)
* **On-Screen Cue:**
  1. Show Step 4.1 (`OBJ.FETCH_METADATA(OBJ.MAKE_REF(gcs_image_uri))`) returning `content_type = image/png` and byte sizes.
  2. Highlight `output_schema => 'condition_grade STRING, detected_hazards ARRAY<STRING>, urgent_remediation BOOL, est_repair_cost_usd INT64, underwriting_summary STRING'` in Step 4.2 and the horizontal repair-cost bar chart.
* **Talk Track:**
  > *"Now watch how BigQuery bridges structured tables and Cloud Storage imagery. `OBJ.MAKE_REF` turns each `gs://` URI into a governed `ObjectRef` struct—and when called with a single URI argument, it uses **Direct Access**, which works cleanly inside **VPC Service Controls** perimeters without generating external HTTPS signed URLs. We pass that `ObjectRef` directly into `AI.GENERATE` with a typed `output_schema`. Instead of brittle free-text paragraphs, Gemini returns native SQL `BOOL`, `INT64`, and `ARRAY<STRING>` columns—immediately flagging `PROP-1002` (hail roof damage) and `PROP-1003` (active ceiling water intrusion) for urgent remediation reserves."*

---

### Step 5: Semantic Work-Order Triage (`AI.IF` + `AI.CLASSIFY`) (3 min)
* **On-Screen Cue:** Point to `REQ-5006` (*"dishwasher leaves water spots... unit is **not** leaking"*) vs. `REQ-5007` (*"electrical subpanel buzzing arcing sound and burnt plastic smell"*) and `REQ-5009` (*"water heater ruptured... flooding hallway"*), plus the stacked vendor trade bar chart.
* **Talk Track:**
  > *"Every property management platform struggles with resident maintenance text. A keyword rule like `LIKE '%leak%'` triggers a false-positive emergency on `REQ-5006` where the resident wrote 'unit is **not** leaking', while completely missing `REQ-5007` where a breaker panel smells like burning plastic! BigQuery's managed `AI.IF` function evaluates semantic intent—calibrated with three inline few-shot `examples`—and returns a true SQL `BOOL` for 24-hour emergency dispatch. In the exact same `SELECT`, `AI.CLASSIFY` routes every ticket into our five exact vendor trade queues with zero post-processing."*

---

### Step 6: Zero-Shot Regional Rent Roll Forecasting (`AI.FORECAST`) (3 min)
* **On-Screen Cue:** Show the `AI.EVALUATE` holdout accuracy table (Step 6.1) followed by the **2×3 multi-metro TimesFM fan chart** (Step 6.2).
* **Talk Track:**
  > *"Next, how are our six markets trending over the next 12 months? Notice there is **no `CREATE MODEL` statement** anywhere in Step 6. `AI.FORECAST` calls Google's pre-trained **TimesFM** time-series foundation model zero-shot across all 12 `(metro_area, property_type)` series in one query via `id_cols`. We validate accuracy honestly on a 12-month chronological holdout with `AI.EVALUATE`, then project 12 months forward with 95% confidence bands—capturing summer leasing peaks and metro growth trajectories out of the box."*

---

### Step 7: Zero-Shot Fair-Market Rent & Churn Prediction (`AI.PREDICT`) (4 min)
* **On-Screen Cue:** Highlight the `AI.PREDICT` SQL block (passing the `TRAIN` comps query and `properties` prediction query with `label_col => 'market_monthly_rent_usd'` and `label_col => 'lease_renewal_outcome'`) and the scatter plot of **In-Place Rent vs. TabFM Fair-Market Rent**.
* **Talk Track:**
  > *"Step 7 showcases `AI.PREDICT` (Public Preview), powered by **TabFM**—Google's foundation model for structured tabular data. Normally, building both a hedonic rent valuation regressor and a tenant-churn classifier requires feature pipelines, encoding categoricals, training two separate models, and scheduling retraining jobs. With `AI.PREDICT`, we pass 300 comparable leases as in-context examples at query time: numeric `label_col` runs regression to surface legacy leases sitting \$250–\$350/month below market, and string `label_col` runs classification returning calibrated churn probabilities!"*

---

### Step 8: Executive Action Synthesis & OKF Policy Guardrails (2 min)
* **On-Screen Cue:** Show the final 6-property executive table where `PROP-1002` and `PROP-1003` automatically enforce `okf_approved_renewal_increase_pct = 0.0%` (`HOLD RENT & DISPATCH`), while hazard-free under-rented properties cap increases at `<= 8.0%`.
* **Talk Track:**
  > *"Finally, Step 8 joins every modality in one SQL query. Without cross-modal context, an automated pricing tool might push a rent increase on `PROP-1002` in Denver right after hail tore off its shingles—guaranteeing tenant churn or regulatory exposure. Because our roof vision results, maintenance tickets, TimesFM market growth, TabFM rent valuation, and OKF policy rules all live in BigQuery, we deterministically freeze rent increases at `0%` on hazard-flagged homes, trigger 24-hour vendor dispatch, and send right-sized renewal offers on clean, under-rented properties."*

---

## 3. Presenter Q&A Cheat Sheet ("If Asked")

1. **"`AI.GENERATE` vs. `ML.GENERATE_TEXT` / `AI.GENERATE_TEXT` — which should Cotality standardize on?"**
   * Standardize new SQL development on **`AI.GENERATE`** (plus task-specific **`AI.IF`** and **`AI.CLASSIFY`**). `AI.GENERATE` operates row-by-row as a scalar SQL expression (no `CREATE REMOTE MODEL` boilerplate required when using end-user credentials or direct `endpoint` arguments), natively accepts multimodal `(text, ObjectRef)` tuples, and enforces structured typed BigQuery columns via `output_schema`. `AI.GENERATE_TEXT` / `ML.GENERATE_TEXT` are table-valued functions designed around `CREATE MODEL ... REMOTE WITH CONNECTION` workflows.
2. **"How does `OBJ.MAKE_REF` work inside strict VPC Service Controls (VPC-SC) perimeters?"**
   * Calling single-argument **`OBJ.MAKE_REF(gcs_uri)`** uses **Direct Access**, passing the `gs://` URI directly to Gemini within your VPC-SC perimeter rather than generating an external signed HTTPS URL (which VPC-SC blocks).
3. **"How do we control LLM costs when running `AI.IF` or `AI.CLASSIFY` across millions of historical maintenance tickets?"**
   * Filter with cheap SQL predicates first (`WHERE status = 'OPEN'` or incremental partition filters on `request_date`), materialize outputs into partitioned tables rather than re-evaluating in BI views, and for massive batch backfills enable `AI.IF` / `AI.CLASSIFY` **`optimization_mode => 'MINIMIZE_COST'`** with materialized embeddings (`AI.EMBED`), which trains a lightweight distilled classifier on Gemini labels to cut token spend dramatically.
4. **"When should we use zero-shot `AI.PREDICT` (TabFM) vs. `CREATE MODEL` (`BOOSTED_TREE_REGRESSOR` / `DNN`)?"**
   * `AI.PREDICT` (Public Preview, up to 50 feature columns and up to 10 classes) excels at rapid prototyping, cold-start sub-markets, ad-hoc analyst valuations, and dynamic cohort comparisons with zero MLOps overhead. When feature counts exceed 50, training rows reach tens of millions, or strict sub-millisecond serving / custom explainability (`ML.EXPLAIN_PREDICT`) is required, graduate the proven feature set to a trained BigQuery ML Boosted Tree or Vertex AI endpoint.
