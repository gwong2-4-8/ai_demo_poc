# Cotality — Tailored BigQuery Architecture & FinOps Best Practices (Slide 23)

- **Presentation**: [[Cotality] BigQuery Workshop - WIP — Slide 23](https://docs.google.com/presentation/d/1FcI4hcXC27KKj0m-CA2eaEux8psIb5gZwNN1pBDP5C8/edit#slide=id.cotality_bq_bp_s23)
- **Section Placement**: Closes Section `02 BigQuery Architecture (Editions, Best Practice)` immediately after Slide 22 (*BigQuery Optimizer Features*) and right before Slide 24 (*Break*).
- **Rendered Slide PNG**: [cotality_bq_best_practices_slide.png](file:///usr/local/google/home/cannis/ace/cotality/cotality_bq_best_practices_slide.png)

---

## 1. Slide Copy (Cloudstyle 2.0 2×2 Pillar Grid + 30-Day Focus Bar)

**Kicker**: `BIGQUERY ARCHITECTURE & FINOPS BEST PRACTICES · TAILORED FOR COTALITY`
**Action Title**: **Maximize Enterprise Commit Efficiency Across Compute, Storage & AI**
**Subtitle**: Actionable architecture rules aligned to hybrid On-Demand + Editions compute, property storage compression, US/AU pipelines & governed AI

### Pillar 01 — Hybrid Compute & Commit Agility
- **Scale Enterprise Edition**: Shift steady ETL & high-concurrency Looker BI off per-TiB On-Demand to autoscaling + `Fluid Scaling`.
- **Guard Ad-Hoc On-Demand**: Enforce `maximum_bytes_billed`, `require_partition_filter` & `Optional Job Creation Mode`.
- **Flexible Commit Pacing**: Keep EA spend flexible first; evaluate 1yr/3yr slot commits only on proven 24×7 troughs.

### Pillar 02 — Physical Storage & Time Travel
- **Audit >2:1 Break-Even**: Profile `TABLE_STORAGE_BY_ORGANIZATION` (with Time Travel + 7d Fail-Safe) on property & geo tables.
- **Tune Time Travel First**: Lower `max_time_travel_hours` (`168 -> 48`) on high-churn ETL staging before switching models.
- **Hybrid Dataset Billing**: Move high-compression datasets to `PHYSICAL`; keep low-compression append tables on `LOGICAL` (`-50%` after 90 days).

### Pillar 03 — Write API & US / AU Data Locality
- **Adopt `Storage Write API`**: Replace paid `insertAll` streams (Dataflow/PubSub) for `2 TiB/mo` free quota & exactly-once IO.
- **Push Down ELT Compute**: Shift heavy Dataflow joins & aggregations into BigQuery SQL (`Advanced Runtime + HBO`) to cut shuffle.
- **Align Regional Gravity**: Co-locate GCS, Dataflow workers & BQ datasets in `us`, regional & Sydney (`australia-southeast1`) hubs to avoid cross-region egress.

### Pillar 04 — Multi-Project BI & AI Governance
- **Central Admin Reservations**: Pool slots across projects with user-based assignments isolating Looker BI, DocAI/ETL & Ad-Hoc.
- **Semantic SQL Pruning**: Ground Looker & Conversational Analytics in `Knowledge Catalog` so NL2SQL hits partition/cluster keys.
- **Optimized Native AI**: Enable `optimize_mode` on `AI.IF` / `AI.CLASSIFY` pipelines and track slot ROI via `JOBS_BY_ORGANIZATION`.

### Bottom Bar — `30-DAY FOCUS`
1. **① Storage Compression Audit**: Tune 48h Time Travel; flip `>2:1` datasets
2. **② Hybrid Compute Sizing**: Benchmark Fluid Scaling + scan caps
3. **③ Governed BI & AI Pools**: Admin Reservations + Knowledge Catalog

---

## 2. Tripartite Speaker Notes & Customer Audit SQL

**[PURPOSE]**
Close Section 02 (*BigQuery Architecture & Best Practice*) by synthesizing how BigQuery's compute, storage, ingestion, and governance primitives fit together for Cotality's real-world operating model and Enterprise Agreement flexibility.

**[VERBAL SCRIPT]**
> "Before we head into break, let's bring Section 02 together into four architectural best practices tailored directly to how Cotality runs data and AI across regions and projects. First, on compute: keep migrating steady ETL and high-concurrency Looker workloads onto Enterprise Edition autoscaling with Fluid Scaling, while keeping scan guardrails on ad-hoc On-Demand queries so every Enterprise Agreement dollar stretches further before locking into rigid slot commitments. Second, on storage: property, tax, and geospatial tables typically compress four-to-ten-X in Capacitor—audit `TABLE_STORAGE_BY_ORGANIZATION`, tune Time Travel down to 48 hours on high-churn staging datasets, and transition datasets above the two-to-one compression break-even to Physical Storage billing. Third, modernize legacy streaming pipelines onto the Storage Write API and keep US and Australia pipelines region-aligned with SQL pushdown to eliminate cross-region egress and unnecessary shuffle. Finally, pool capacity in a central Admin Project using dynamic user-based reservations integrated with Knowledge Catalog so Looker, batch pipelines, and Conversational Analytics share governed, pruned SQL cleanly."

**[TRANSITION]**
> "Let's take a quick break, and when we come back in Section 04 we'll see these exact governed tables and optimized AI functions—like `AI.IF`, `AI.CLASSIFY`, and `AI.GENERATE`—running live on residential property data."

**[DATA SOURCE / QUERY]**

```sql
-- Copyright 2026 Google LLC
-- SPDX-License-Identifier: Apache-2.0

-- 1. Dataset Compression & Physical Billing Break-Even Audit (includes Time Travel + 7-day Fail-Safe):
SELECT
  table_schema,
  ROUND(SUM(total_logical_bytes) / POW(1024, 4), 2) AS logical_tib,
  ROUND(SUM(total_physical_bytes) / POW(1024, 4), 2) AS physical_incl_tt_fs_tib,
  ROUND(SAFE_DIVIDE(SUM(total_logical_bytes), SUM(total_physical_bytes)), 2) AS effective_compression_ratio
FROM `region-us`.INFORMATION_SCHEMA.TABLE_STORAGE_BY_ORGANIZATION
WHERE total_logical_bytes > 0
GROUP BY table_schema
HAVING effective_compression_ratio > 2.0
ORDER BY logical_tib DESC;

-- 2. Top On-Demand Scan & Slot Profile Across Projects (30-Day Lookback):
SELECT
  project_id,
  reservation_id,
  COUNT(*) AS job_count,
  ROUND(SUM(total_bytes_billed) / POW(1024, 4), 2) AS tib_billed,
  ROUND(SUM(total_slot_ms) / (1000 * 3600), 1) AS slot_hours
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
GROUP BY 1, 2
ORDER BY tib_billed DESC
LIMIT 25;
```

---

## 3. Official Google Cloud Documentation References

- [Introduction to BigQuery Editions & Autoscaling](https://cloud.google.com/bigquery/docs/editions-intro)
- [Dataset Storage Billing Models (`LOGICAL` vs. `PHYSICAL` & Time Travel)](https://cloud.google.com/bigquery/docs/datasets-intro#dataset_storage_billing_models)
- [BigQuery Storage Write API Best Practices](https://cloud.google.com/bigquery/docs/write-api-best-practices)
- [Estimate and Control Costs in BigQuery](https://cloud.google.com/bigquery/docs/best-practices-costs)
- [Workload Management Using Reservations (`ADMIN` Project Architecture)](https://cloud.google.com/bigquery/docs/reservations-workload-management)
