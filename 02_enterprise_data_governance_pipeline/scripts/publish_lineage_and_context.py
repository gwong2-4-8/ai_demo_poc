#!/usr/bin/env python3
# Copyright 2026 Google LLC
# SPDX-License-Identifier: Apache-2.0
"""Publishes Cloud SQL -> BigQuery lineage, governance aspects, and glossary entry links in Knowledge Catalog."""

import datetime
import json
import subprocess
import urllib.error
import urllib.request

PROJECT_ID = "demo1-371900"
PROJECT_NUMBER = "477924732837"
LOCATION = "us-west1"


def get_headers():
    token = subprocess.check_output(
        ["gcloud", "auth", "print-access-token", "--quiet"], text=True
    ).strip()
    return {
        "Authorization": f"Bearer {token}",
        "X-Goog-User-Project": PROJECT_ID,
        "Content-Type": "application/json",
    }


def api_call(method, url, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def publish_lineage(headers):
    now = datetime.datetime.now(datetime.timezone.utc)
    start_ts = (now - datetime.timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_ts = (now - datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    base = f"https://datalineage.googleapis.com/v1/projects/{PROJECT_NUMBER}/locations/{LOCATION}"

    jobs = [
        {
            "display_name": "ingram_cloudsql_to_bq_products_elt",
            "sql": (
                'CREATE OR REPLACE TABLE `demo1-371900.ingram_micro_analytics.products` AS '
                'SELECT * FROM EXTERNAL_QUERY("projects/demo1-371900/locations/us-west1/connections/ingram-cloudsql-conn", '
                '"SELECT sku, product_name, vendor, category, unit_cost_usd, unit_price_usd, active, updated_at FROM public.products;");'
            ),
            "source_fqn": "cloudsql_postgresql:demo1-371900.us-west1.ingram-catalog-sql.ingram_catalog.public.products",
            "target_fqn": "bigquery:demo1-371900.ingram_micro_analytics.products",
        },
        {
            "display_name": "ingram_cloudsql_to_bq_transactions_elt",
            "sql": (
                'CREATE OR REPLACE TABLE `demo1-371900.ingram_micro_analytics.product_transactions` AS '
                'SELECT * FROM EXTERNAL_QUERY("projects/demo1-371900/locations/us-west1/connections/ingram-cloudsql-conn", '
                '"SELECT transaction_id, sku, reseller_name, sales_region, quantity, discount_pct, transaction_ts, order_status FROM public.product_transactions;");'
            ),
            "source_fqn": "cloudsql_postgresql:demo1-371900.us-west1.ingram-catalog-sql.ingram_catalog.public.product_transactions",
            "target_fqn": "bigquery:demo1-371900.ingram_micro_analytics.product_transactions",
        },
    ]

    for job in jobs:
        st, proc = api_call(
            "POST",
            f"{base}/processes",
            {
                "displayName": job["display_name"],
                "origin": {
                    "sourceType": "CUSTOM",
                    "name": "bigquery-cloudsql-federated-elt",
                },
                "attributes": {"sql": job["sql"]},
            },
            headers,
        )
        print(f"Create process ({job['display_name']}): {st}")
        proc_name = proc["name"]

        st, run = api_call(
            "POST",
            f"https://datalineage.googleapis.com/v1/{proc_name}/runs",
            {
                "displayName": f"{job['display_name']}_initial_load",
                "startTime": start_ts,
                "endTime": end_ts,
                "state": "COMPLETED",
            },
            headers,
        )
        print(f"Create run: {st}")
        run_name = run["name"]

        st, ev = api_call(
            "POST",
            f"https://datalineage.googleapis.com/v1/{run_name}/lineageEvents",
            {
                "startTime": start_ts,
                "endTime": end_ts,
                "links": [
                    {
                        "source": {"fullyQualifiedName": job["source_fqn"]},
                        "target": {"fullyQualifiedName": job["target_fqn"]},
                    }
                ],
            },
            headers,
        )
        print(f"Create lineageEvent ({job['source_fqn']} -> {job['target_fqn']}): {st}")


def create_glossary_links(headers):
    dp_base = f"https://dataplex.googleapis.com/v1/projects/{PROJECT_NUMBER}/locations/{LOCATION}/entryGroups/@dataplex/entryLinks"
    links = [
        (
            "link-sku-products",
            f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/entryGroups/@bigquery/entries/bigquery.googleapis.com/projects/{PROJECT_ID}/datasets/ingram_micro_analytics/tables/products",
            "Schema.sku",
            f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/entryGroups/@dataplex/entries/projects/{PROJECT_NUMBER}/locations/{LOCATION}/glossaries/ingram-micro-glossary/terms/catalog-sku",
        ),
        (
            "link-sku-transactions",
            f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/entryGroups/@bigquery/entries/bigquery.googleapis.com/projects/{PROJECT_ID}/datasets/ingram_micro_analytics/tables/product_transactions",
            "Schema.sku",
            f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/entryGroups/@dataplex/entries/projects/{PROJECT_NUMBER}/locations/{LOCATION}/glossaries/ingram-micro-glossary/terms/catalog-sku",
        ),
        (
            "link-gross-rev-summary",
            f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/entryGroups/@bigquery/entries/bigquery.googleapis.com/projects/{PROJECT_ID}/datasets/ingram_micro_analytics/tables/sku_revenue_summary",
            "Schema.gross_catalog_revenue_usd",
            f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/entryGroups/@dataplex/entries/projects/{PROJECT_NUMBER}/locations/{LOCATION}/glossaries/ingram-micro-glossary/terms/gross-catalog-revenue",
        ),
        (
            "link-net-rev-summary",
            f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/entryGroups/@bigquery/entries/bigquery.googleapis.com/projects/{PROJECT_ID}/datasets/ingram_micro_analytics/tables/sku_revenue_summary",
            "Schema.net_recognized_revenue_usd",
            f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/entryGroups/@dataplex/entries/projects/{PROJECT_NUMBER}/locations/{LOCATION}/glossaries/ingram-micro-glossary/terms/net-recognized-revenue",
        ),
        (
            "link-margin-summary",
            f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/entryGroups/@bigquery/entries/bigquery.googleapis.com/projects/{PROJECT_ID}/datasets/ingram_micro_analytics/tables/sku_revenue_summary",
            "Schema.distributor_gross_margin_usd",
            f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/entryGroups/@dataplex/entries/projects/{PROJECT_NUMBER}/locations/{LOCATION}/glossaries/ingram-micro-glossary/terms/distributor-gross-margin",
        ),
    ]
    for link_id, target_entry, col_path, term_entry in links:
        st, out = api_call(
            "POST",
            f"{dp_base}?entryLinkId={link_id}",
            {
                "entryLinkType": "projects/dataplex-types/locations/global/entryLinkTypes/definition",
                "entryReferences": [
                    {"name": target_entry, "path": col_path, "type": "TARGET"},
                    {"name": term_entry, "type": "SOURCE"},
                ],
            },
            headers,
        )
        print(f"Create glossary entryLink ({link_id}): {st}")
        if st >= 400:
            print("   detail:", str(out)[:300])


def verify_lineage(headers):
    base = f"https://datalineage.googleapis.com/v1/projects/{PROJECT_NUMBER}/locations/{LOCATION}:searchLinks"
    for fqn in [
        "bigquery:demo1-371900.ingram_micro_analytics.products",
        "bigquery:demo1-371900.ingram_micro_analytics.product_transactions",
        "bigquery:demo1-371900.ingram_micro_analytics.sku_revenue_summary",
    ]:
        st, out = api_call("POST", base, {"target": {"fullyQualifiedName": fqn}}, headers)
        print(f"Upstream links for {fqn} ({st}):", json.dumps(out))


if __name__ == "__main__":
    hdrs = get_headers()
    publish_lineage(hdrs)
    create_glossary_links(hdrs)
    verify_lineage(hdrs)
