#!/usr/bin/env python3
# Copyright 2026 Google LLC
# SPDX-License-Identifier: Apache-2.0
"""Publishes Data Quality lineage and certified governance aspect for dq_scan_results."""

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


def attach_governance_aspect(headers):
    entry_url = (
        f"https://dataplex.googleapis.com/v1/projects/{PROJECT_NUMBER}/locations/{LOCATION}"
        f"/entryGroups/@bigquery/entries/bigquery.googleapis.com/projects/{PROJECT_ID}"
        f"/datasets/ingram_micro_analytics/tables/dq_scan_results"
        f"?updateMask=aspects&aspectKeys={PROJECT_NUMBER}.{LOCATION}.ingram-governance"
    )
    payload = {
        "aspects": {
            f"{PROJECT_NUMBER}.{LOCATION}.ingram-governance": {
                "aspectType": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/aspectTypes/ingram-governance",
                "data": {
                    "certified_status": "CERTIFIED",
                    "business_domain": "Ingram Micro B2B IT Distribution",
                    "data_steward": "admin@cannis.altostrat.com",
                },
            }
        }
    }
    st, out = api_call("PATCH", entry_url, payload, headers)
    print(f"Attach ingram-governance aspect to dq_scan_results: {st}")
    if st >= 400:
        print("  detail:", str(out)[:300])


def publish_dq_lineage(headers):
    now = datetime.datetime.now(datetime.timezone.utc)
    start_ts = (now - datetime.timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_ts = (now - datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    base = f"https://datalineage.googleapis.com/v1/projects/{PROJECT_NUMBER}/locations/{LOCATION}"

    st, proc = api_call(
        "POST",
        f"{base}/processes",
        {
            "displayName": "ingram_knowledge_catalog_auto_dq_export",
            "origin": {
                "sourceType": "CUSTOM",
                "name": "dataplex-auto-data-quality-postscan-export",
            },
            "attributes": {
                "scans": "ingram-products-dq-scan, ingram-transactions-dq-scan",
                "rules_evaluated": "10",
            },
        },
        headers,
    )
    print(f"Create DQ lineage process: {st}")
    proc_name = proc["name"]

    st, run = api_call(
        "POST",
        f"https://datalineage.googleapis.com/v1/{proc_name}/runs",
        {
            "displayName": "auto_dq_scan_bigquery_export_run",
            "startTime": start_ts,
            "endTime": end_ts,
            "state": "COMPLETED",
        },
        headers,
    )
    print(f"Create DQ lineage run: {st}")
    run_name = run["name"]

    links = [
        {
            "source": {"fullyQualifiedName": "bigquery:demo1-371900.ingram_micro_analytics.products"},
            "target": {"fullyQualifiedName": "bigquery:demo1-371900.ingram_micro_analytics.dq_scan_results"},
        },
        {
            "source": {"fullyQualifiedName": "bigquery:demo1-371900.ingram_micro_analytics.product_transactions"},
            "target": {"fullyQualifiedName": "bigquery:demo1-371900.ingram_micro_analytics.dq_scan_results"},
        },
        {
            "source": {"fullyQualifiedName": "bigquery:demo1-371900.ingram_micro_analytics.dq_scan_results"},
            "target": {
                "fullyQualifiedName": "looker_core:view:demo1-371900.us-west1.lookerid1.ingram_micro_catalog.ingram_micro_revenue.dq_scan_results"
            },
        },
        {
            "source": {
                "fullyQualifiedName": "looker_core:view:demo1-371900.us-west1.lookerid1.ingram_micro_catalog.ingram_micro_revenue.dq_scan_results"
            },
            "target": {
                "fullyQualifiedName": "looker_core:explore:demo1-371900.us-west1.lookerid1.ingram_micro_catalog.ingram_micro_revenue.dq_scan_results"
            },
        },
        {
            "source": {
                "fullyQualifiedName": "looker_core:explore:demo1-371900.us-west1.lookerid1.ingram_micro_catalog.ingram_micro_revenue.dq_scan_results"
            },
            "target": {
                "fullyQualifiedName": "looker_core:lookml_dashboard:demo1-371900.us-west1.lookerid1.ingram_micro_catalog.ingram_micro_revenue.ingram_data_quality_scorecard"
            },
        },
        {
            "source": {
                "fullyQualifiedName": "looker_core:explore:demo1-371900.us-west1.lookerid1.ingram_micro_catalog.ingram_micro_revenue.dq_scan_results"
            },
            "target": {
                "fullyQualifiedName": "looker_core:lookml_dashboard:demo1-371900.us-west1.lookerid1.ingram_micro_catalog.ingram_micro_revenue.ingram_revenue_overview"
            },
        },
    ]
    st, ev = api_call(
        "POST",
        f"https://datalineage.googleapis.com/v1/{run_name}/lineageEvents",
        {"startTime": start_ts, "endTime": end_ts, "links": links},
        headers,
    )
    print(f"Create DQ lineage event (products & product_transactions -> dq_scan_results): {st}")

    # Verify downstream Looker lineage from dq_scan_results
    search_url = f"{base}:searchLinks"
    st_dn, dn = api_call(
        "POST",
        search_url,
        {"source": {"fullyQualifiedName": "bigquery:demo1-371900.ingram_micro_analytics.dq_scan_results"}},
        headers,
    )
    print(f"Downstream links from dq_scan_results ({st_dn}):", json.dumps(dn))


if __name__ == "__main__":
    hdrs = get_headers()
    attach_governance_aspect(hdrs)
    publish_dq_lineage(hdrs)
