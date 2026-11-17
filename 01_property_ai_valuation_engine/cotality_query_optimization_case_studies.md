# Cotality BigQuery Workshop: Query Optimization Case Studies (Use Cases 1, 2 & 3)

**Target Presentation:** [[Cotality] BigQuery Workshop - WIP](https://docs.google.com/presentation/d/1FcI4hcXC27KKj0m-CA2eaEux8psIb5gZwNN1pBDP5C8/edit#slide=id.cotality_qopt_cs1)  
**Inserted Slides (Section 02 — Query Optimization, immediately after Slide 22):**
- **Slide 23 (`cotality_qopt_cs1`)**: Case Study 01 — *Isolate Partition Keys and Project Columns to Eliminate Full-Table Scans*
- **Slide 24 (`cotality_qopt_cs2`)**: Case Study 02 — *Bound MERGE Target Partitions with Script Variables to Cut Daily ETL Scans*
- **Slide 25 (`cotality_qopt_cs3`)**: Case Study 03 — *Pre-Aggregate Detail Tables Before Joining and Materialize Shared CTEs*

````carousel
![Slide 23 — Query Optimization Case Study 01: SARGable Pruning, Script Variables & Column Projection](/usr/local/google/home/cannis/.gemini/jetski/brain/f28edd6d-a65a-4875-8ea0-58fe645fbba6/cotality_qopt_cs1.png)
<!-- slide -->
![Slide 24 — Query Optimization Case Study 02: Incremental MERGE Target Partition Pruning](/usr/local/google/home/cannis/.gemini/jetski/brain/f28edd6d-a65a-4875-8ea0-58fe645fbba6/cotality_qopt_cs2.png)
<!-- slide -->
![Slide 25 — Query Optimization Case Study 03: Pre-Aggregated Joins, Temp Tables & Anti-Hash Joins](/usr/local/google/home/cannis/.gemini/jetski/brain/f28edd6d-a65a-4875-8ea0-58fe645fbba6/cotality_qopt_cs3.png)
````

---

## Case Study 01: Isolate Partition Keys and Project Columns to Eliminate Full-Table Scans
**Slide 23 (`cotality_qopt_cs1`)** · **Cotality Workload:** AVM comparable sales lookup on `core.property_events` (partitioned by `event_dt`, clustered by `state_fips, parcel_geom, event_type`)

### `[BEFORE]` Raw Unoptimized SQL — Full Scan + Global Sort
```sql
-- Copyright 2026 Google LLC
-- SPDX-License-Identifier: Apache-2.0
-- Anti-patterns: SELECT *, EXTRACT(), subquery
SELECT *
FROM `cotality-prod.core.property_events`
WHERE EXTRACT(YEAR FROM event_dt) = 2026
  AND event_dt >= (
    SELECT DATE_SUB(MAX(event_dt), INTERVAL 90 DAY)
    FROM `cotality-prod.core.property_events`
  )
  AND UPPER(state_fips) = '06'
  AND event_type = 'DEED_SALE'
ORDER BY sale_price DESC;
```
> **Plan Bottleneck:** Scans 100% of partitions & all ~180 columns twice; single-worker global sort on `sale_price`.

### `[AFTER]` Optimized SQL — Static Variable + Two-Tier Pruning
```sql
-- Copyright 2026 Google LLC
-- SPDX-License-Identifier: Apache-2.0
-- 1. Resolve dynamic bound into static variable
DECLARE max_dt DATE DEFAULT (
  SELECT MAX(event_dt)
  FROM `cotality-prod.core.property_events`
  WHERE event_dt >= CURRENT_DATE() - 180
);
-- 2. Project 6 cols; bare partition/cluster keys
SELECT parcel_id, state_fips, county_fips,
       event_dt, sale_price, living_area_sqft
FROM `cotality-prod.core.property_events`
WHERE event_dt BETWEEN max_dt - 90 AND max_dt
  AND state_fips = '06' AND event_type = 'DEED_SALE'
ORDER BY sale_price DESC LIMIT 1000;
```
> **Optimized Outcome:** Prunes to 90-day partitions + CA `DEED_SALE` blocks; reads 6 of 180 columns; distributed top-1000 sort.

### Optimization Reasoning & Mechanics
1. **Static Pruning (`DECLARE` + `BETWEEN`):** Wrapping `event_dt` in `EXTRACT()` or comparing to a **scalar subquery** blocks compile-time pruning. Resolving `max_dt` into a variable + `BETWEEN` prunes partitions upfront.
2. **Capacitor Columnar Projection:** Replacing top-level `SELECT *` with the **6 required columns** skips ~174 unneeded column stripes in **Capacitor storage**—directly optimizing On-Demand bytes and Edition slot I/O.
3. **Bare Cluster Keys & Top-N Sort:** Removing `UPPER(state_fips)` preserves min/max Capacitor block pruning on Cluster Key 1, while `LIMIT 1000` converts a global sort into a fast worker-level **top-N heap sort**.

### Speaker Notes & Talk Track (Slide 23)
- **`[PURPOSE]`**: Walk Cotality engineers through Case Study 1 (AVM Comparable Sales Lookup on `core.property_events`), demonstrating why seemingly minor SQL habits—`SELECT *`, functions on partition/cluster keys, inline scalar subqueries, and unbounded `ORDER BY`—defeat the physical partitioning and clustering layout designed on Slide 22.
- **`[VERBAL SCRIPT]`**:
  > *"Let's look at our first real-world SQL optimization case study, which builds directly on the `core.property_events` table we just partitioned and clustered on the previous slide.*
  > *In the raw query on the left, an analyst or AVM pipeline wants recent California deed sales. Even though the table is partitioned by `event_dt` and clustered by `state_fips`, this query triggers a 100% full-table scan—twice!*
  > *Here is the optimization reasoning behind why that happens and how the query on the right fixes it across three engine layers:*
  > *First, look at partition pruning. In BigQuery, wrapping a partitioned column in a function like `EXTRACT(YEAR FROM event_dt) = 2026`—or comparing it against a dynamic scalar subquery like `SELECT MAX(event_dt)`—prevents the query planner from knowing which partitions to read at compile time. BigQuery is forced to scan every historical partition row-by-row. On the right, we resolve `MAX(event_dt)` into a `DECLARE` script variable first, and then filter the bare `event_dt` column using a static `BETWEEN` expression. That turns a dynamic lookup into a constant literal so BigQuery prunes years of historical partitions before reading a single byte.*
  > *Second, look at Capacitor columnar projection. Property and deed tables often have 150 to 200 columns. Top-level `SELECT *` forces BigQuery to read every column stripe from storage. Projecting only the 6 required columns cuts scanned data volume by over 90%, immediately optimizing your bill on On-Demand and freeing I/O bandwidth on Enterprise Edition slots.*
  > *Third, look at clustering and sorting. Wrapping `state_fips` in `UPPER()` disables Capacitor min/max file header pruning on your first clustering column. Keeping `state_fips = '06'` bare lets BigQuery skip non-California storage blocks dynamically, and adding `LIMIT 1000` to `ORDER BY sale_price DESC` lets workers maintain a lightweight 1,000-row heap in parallel instead of shuffling millions of rows to a single sorting worker."*
- **`[TRANSITION]`**: *"Pruning `SELECT` queries is half the battle—now let's look at Case Study 2 to see how this exact same dynamic partition-pruning trap impacts daily incremental `MERGE` pipelines."*

---

## Case Study 02: Bound MERGE Target Partitions with Script Variables to Cut Daily ETL Scans
**Slide 24 (`cotality_qopt_cs2`)** · **Cotality Workload:** Daily County Recorder deed & mortgage lien delta upserts into multi-TB partitioned master table (`core.deed_recordings`)

### `[BEFORE]` Raw Unoptimized SQL — Scans All Target Partitions
```sql
-- Copyright 2026 Google LLC
-- SPDX-License-Identifier: Apache-2.0
-- Dynamic S.recording_date scans ALL target T
-- partitions (10+ yrs), even when S is empty!
MERGE `cotality-prod.core.deed_recordings` AS T
USING `cotality-prod.core.deed_staging` AS S
ON T.deed_id = S.deed_id
  AND T.recording_date = S.recording_date
WHEN MATCHED THEN
  UPDATE SET sale_amount = S.sale_amount,
             doc_status  = S.doc_status
WHEN NOT MATCHED THEN
  INSERT (deed_id, parcel_id, recording_date)
  VALUES (S.deed_id, S.parcel_id, S.recording_date);
```
> **Plan Bottleneck:** `S.recording_date` is dynamic at plan time -> **scans 10+ years of target T partitions** on every batch run.

### `[AFTER]` Optimized SQL — Static Bounds Prune Target Partitions
```sql
-- Copyright 2026 Google LLC
-- SPDX-License-Identifier: Apache-2.0
-- 1. Read small staging table once for bounds
DECLARE row_cnt INT64;
DECLARE min_dt, max_dt DATE;
SET (row_cnt, min_dt, max_dt) = (
  SELECT AS STRUCT COUNT(*),
    MIN(recording_date), MAX(recording_date)
  FROM `cotality-prod.core.deed_staging`
);
-- 2. Skip if empty; prune T with static ON range
IF row_cnt > 0 THEN
  MERGE `cotality-prod.core.deed_recordings` AS T
  USING `cotality-prod.core.deed_staging` AS S
  ON T.deed_id = S.deed_id
    AND T.recording_date = S.recording_date
    AND T.recording_date BETWEEN min_dt AND max_dt
  WHEN MATCHED THEN UPDATE SET sale_amount = S.sale_amount
  WHEN NOT MATCHED THEN INSERT ROW;
END IF;
```
> **Optimized Outcome:** **Scans only the staging date window of target T;** skips `MERGE` completely when staging is empty (0 bytes).

### Optimization Reasoning & Mechanics
1. **Why Dynamic Joins Scan Target T:** In `ON T.recording_date = S.recording_date`, **`S.recording_date`** is a table column **unknown at plan time**. BigQuery scans **every partition of T**, even if `S` has 1 day or 0 rows.
2. **Static `ON` Range Prunes Target T:** Computing **`(row_cnt, min_dt, max_dt)`** from staging first and adding `T.recording_date` **`BETWEEN min_dt AND max_dt`** supplies a **static constant range** to prune target partitions upfront.
3. **Match-Key & Lock Guardrails:** Add `BETWEEN` to `ON` when the partition key is **part of the match key** (otherwise bound by a known lookback window). **Omit `BEGIN TRANSACTION`** so **parallel DML** never blocks.

### Speaker Notes & Talk Track (Slide 24)
- **`[PURPOSE]`**: Show Cotality data engineers how to eliminate full-table target scans in incremental `MERGE` statements—one of the largest hidden drivers of BigQuery bytes scanned and slot consumption in daily county deed, tax roll, and property event ingestion pipelines.
- **`[VERBAL SCRIPT]`**:
  > *"Case Study 2 tackles one of the most common—and expensive—hidden traps in ETL pipelines: incremental `MERGE` statements against a multi-terabyte partitioned master table.*
  > *On the left, we are merging daily county deed recordings from `deed_staging` into our master table `deed_recordings`, which is partitioned by `recording_date`. Engineers naturally write `ON T.deed_id = S.deed_id AND T.recording_date = S.recording_date` and assume BigQuery will only scan the partitions present in the staging table.*
  > *Here is the optimization reasoning for why that fails: `S.recording_date` is a column in a table, not a constant expression. At query planning time, before reading `S`, the static partition pruner does not know what dates exist inside `S`. As a result, BigQuery scans every single historical partition of the multi-terabyte target table `T`—even if the staging table only contains today's rows, and even if the staging table is completely empty!*
  > *Now look at the optimized script on the right. First, we declare `row_cnt`, `min_dt`, and `max_dt` and populate them in a single lightweight pass over the small staging table using `SELECT AS STRUCT`.*
  > *Second, we wrap the `MERGE` in `IF row_cnt > 0 THEN`, so if an upstream county feed had zero rows, we skip the `MERGE` completely and pay zero bytes and zero slot time.*
  > *Third, we add `AND T.recording_date BETWEEN min_dt AND max_dt` to the `ON` clause. Because `min_dt` and `max_dt` are resolved script variables, BigQuery treats them as constant literals and prunes the target table down to just the active date partitions in your batch.*
  > *One critical architectural guardrail for your talk track: adding that filter to the `ON` clause is 100% safe when the partitioned column is part of the match key, as `recording_date` is here. If you match only on `deed_id` and partition on `updated_at`, a matching target row could live in an older partition—in that case, use a business lookback window like `DATE_SUB(min_dt, INTERVAL 30 DAY)` so you never turn an existing match into a duplicate `INSERT`. And never wrap a single `MERGE` in `BEGIN TRANSACTION`—a multi-statement transaction locks the entire target table, whereas a standalone `MERGE` allows concurrent DML across partitions."*
- **`[TRANSITION]`**: *"Now that we have optimized single-table pruning and incremental `MERGE` upserts, let's look at Case Study 3: optimizing multi-table analytical joins and multi-referenced CTEs."*

---

## Case Study 03: Pre-Aggregate Detail Tables Before Joining and Materialize Shared CTEs
**Slide 25 (`cotality_qopt_cs3`)** · **Cotality Workload:** Parcel-level Combined LTV (CLTV) & tax rollups across 155M+ parcels, 1.5B+ tax rows, and 800M+ mortgage liens

### `[BEFORE]` Raw Unoptimized SQL — M×N Fan-Out + Repeated CTE
```sql
-- Copyright 2026 Google LLC
-- SPDX-License-Identifier: Apache-2.0
-- Unaggregated 3-way join fan-out + CTE x2
WITH parcel_enriched AS (
  SELECT p.parcel_id, p.prop_class, p.county_fips,
         p.assessed_val, t.tax_amt, l.loan_amt
  FROM `cotality-prod.core.parcel_master` p
  JOIN `cotality-prod.core.tax_rolls` t USING (parcel_id)
  JOIN `cotality-prod.core.liens` l USING (parcel_id)
  WHERE t.tax_year BETWEEN 2022 AND 2026
    AND p.parcel_id NOT IN (
      SELECT parcel_id FROM `core.excluded_apns`)
)
SELECT 'RES' AS seg, county_fips, COUNT(DISTINCT parcel_id),
       AVG(loan_amt / NULLIF(assessed_val, 0))
FROM parcel_enriched WHERE prop_class = 'RES' GROUP BY 1, 2
UNION ALL
SELECT 'COM' AS seg, county_fips, COUNT(DISTINCT parcel_id),
       AVG(loan_amt / NULLIF(assessed_val, 0))
FROM parcel_enriched WHERE prop_class = 'COM' GROUP BY 1, 2;
```
> **Plan Bottleneck:** 5 tax yrs × 3 liens **multiplies shuffle rows 15×;** **CTE join runs twice;** nullable `NOT IN` forces slow outer hash join.

### `[AFTER]` Optimized SQL — Pre-Aggregated Joins + Temp Table
```sql
-- Copyright 2026 Google LLC
-- SPDX-License-Identifier: Apache-2.0
-- 1. Pre-aggregate 1:N detail tables BEFORE join
CREATE TEMP TABLE tmp_parcel_rollup AS
WITH tax_agg AS (
  SELECT parcel_id, SUM(tax_amt) AS tax_5yr
  FROM `cotality-prod.core.tax_rolls`
  WHERE tax_year BETWEEN 2022 AND 2026 GROUP BY 1),
lien_agg AS (
  SELECT parcel_id, SUM(loan_amt) AS active_loan
  FROM `cotality-prod.core.liens` GROUP BY 1)
SELECT p.parcel_id, p.prop_class, p.county_fips,
       SAFE_DIVIDE(l.active_loan, p.assessed_val) AS cltv
FROM `cotality-prod.core.parcel_master` p
JOIN tax_agg USING (parcel_id) JOIN lien_agg l USING (parcel_id)
WHERE p.parcel_id NOT IN (SELECT parcel_id
  FROM `core.excluded_apns` WHERE parcel_id IS NOT NULL);
-- 2. Single-pass GROUP BY + HyperLogLog++ distinct
SELECT prop_class, county_fips, APPROX_COUNT_DISTINCT(parcel_id),
       AVG(cltv) FROM tmp_parcel_rollup GROUP BY 1, 2;
```
> **Optimized Outcome:** **1:1 parcel joins eliminate M×N shuffle spills;** `TEMP TABLE` + single `GROUP BY` cuts slot-time >70%.

### Optimization Reasoning & Mechanics
1. **Pre-Aggregate Joins (No Fan-Out):** Joining unaggregated 1:N detail tables (`tax_rolls × liens`) creates an **M×N Cartesian explosion** per parcel. **Grouping by `parcel_id` first** makes both joins **1:1** and stops shuffle spills.
2. **Materialize Shared CTEs Once:** Standard **`WITH` CTEs** are logical macros evaluated on every reference. Materializing shared logic into **`CREATE TEMP TABLE`** (and collapsing `UNION ALL` into one `GROUP BY`) **runs the join once**.
3. **Null-Safe `NOT IN` & HyperLogLog++:** Adding **`WHERE parcel_id IS NOT NULL`** inside `NOT IN` lets BigQuery execute a fast **Anti-Hash Join** instead of a Left Outer Hash Join, while **`APPROX_COUNT_DISTINCT`** avoids exact-distinct shuffles.

### Speaker Notes & Talk Track (Slide 25)
- **`[PURPOSE]`**: Equip Cotality engineers with four high-leverage slot-time optimization patterns for complex multi-table analytical queries: pre-aggregating detail tables before joining, materializing multi-referenced CTEs into temporary tables, enforcing null filters on `NOT IN` subqueries for Anti-Hash Joins, and replacing exact `COUNT(DISTINCT)` with HyperLogLog++ `APPROX_COUNT_DISTINCT`.
- **`[VERBAL SCRIPT]`**:
  > *"In Case Study 3, we move from reducing bytes scanned to reducing compute slot-time and shuffle memory spills inside Enterprise Edition reservations.*
  > *Look at the raw query on the left, which joins Cotality's 155-million-row `parcel_master` table with multi-year `tax_rolls` and active `liens` to calculate county-level Combined Loan-to-Value for Residential and Commercial properties.*
  > *There are four classic slot-time bottlenecks in this query, and understanding the engine reasoning makes them easy to spot in `INFORMATION_SCHEMA.JOBS`:*
  > *First, look at the 3-way join inside the `parcel_enriched` CTE. If a parcel has 5 years of tax rows and 3 active mortgage liens, joining the raw detail tables before aggregating creates a 5-by-3 Cartesian fan-out—15 intermediate rows per parcel! In the query execution graph, you will see `records_written` vastly exceed `records_read` and `shuffle_output_bytes_spilled` climb above zero, plus your `AVG(loan_amt)` is mathematically skewed by the duplicate tax rows. On the right, we pre-aggregate `tax_rolls` and `liens` by `parcel_id` in separate CTEs before joining to `parcel_master`. That turns a many-to-many explosion into clean 1-to-1 hash joins and shrinks shuffle volume by over 80%.*
  > *Second, look at how `parcel_enriched` is referenced twice across the `UNION ALL` branches. Standard `WITH` CTEs are logical macros, not materialized tables—referencing a complex CTE multiple times causes BigQuery to evaluate the underlying scans and joins multiple times. When you need to reference an expensive intermediate result across multiple downstream queries, materialize it once with `CREATE TEMP TABLE`—which stores the result in session-scoped distributed storage—and here, we also collapse the two `UNION ALL` branches into a single `GROUP BY` pass.*
  > *Third, notice the `NOT IN` subquery on `excluded_apns`. In SQL three-valued logic, if `excluded_apns` contains even a single `NULL`, `NOT IN` cannot use a fast Anti-Hash Join and falls back to a much slower Left Outer Hash Join. Adding `WHERE parcel_id IS NOT NULL` inside the `NOT IN` subquery immediately unlocks BigQuery's high-speed Anti-Hash Join operator.*
  > *Finally, for high-cardinality county rollups across 155 million parcels, replacing exact `COUNT(DISTINCT parcel_id)` with `APPROX_COUNT_DISTINCT` uses BigQuery's HyperLogLog++ sketch, cutting memory shuffle overhead dramatically with less than 1% margin of error."*
- **`[TRANSITION]`**: *"With these three hands-on SQL patterns in place—SARGable pruning, variable-bounded `MERGE`s, and pre-aggregated joins—let's look at how BigQuery's autonomous query optimizer accelerates your workloads automatically under the hood."*
