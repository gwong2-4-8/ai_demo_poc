# Google Cloud AI & Data Engineering Internship Portfolio (`ai_demo_poc`)

A collection of enterprise-grade cloud AI, data engineering, and business intelligence proof-of-concept (PoC) projects developed on **Google Cloud Platform (GCP)**.

This repository serves as a capstone internship project showcase demonstrating end-to-end design, implementation, and deployment across modern data platforms, generative AI foundation models, serverless web applications, and automated governance operating models.

---

## 🚀 Showcase Projects

| Project | Primary Focus | Key Technologies |
| :--- | :--- | :--- |
| **[`01_property_ai_valuation_engine`](./01_property_ai_valuation_engine)** | In-database multimodal AI, zero-shot tabular valuation, and time-series forecasting engine with an interactive web UI. | BigQuery AI/ML, Gemini Multimodal SQL, TimesFM, TabFM, Streamlit, Cloud Run, Docker |
| **[`02_enterprise_data_governance_pipeline`](./02_enterprise_data_governance_pipeline)** | End-to-end operational-to-analytical data pipeline with automated data quality governance, 5-hop lineage, and semantic BI dashboards. | Cloud SQL (PostgreSQL), BigQuery Federated ELT, Dataplex Auto DQ, Knowledge Catalog, Looker / LookML |

---

## 📌 Project Summaries

### [Project 1: Real Estate Property AI & Valuation Engine](./01_property_ai_valuation_engine)
An in-database artificial intelligence system designed for real estate investment and property valuation.
- **Multimodal Visual Inspection**: Leverages BigQuery Object Tables and Gemini multimodal models in GoogleSQL to extract architectural style, curb appeal scores, and structural condition directly from GCS exterior photos.
- **Foundation Time-Series Forecasting**: Evaluates and deploys Google's zero-training `TimesFM` foundation model to project 12-month median price and rental growth trajectories across metropolitan areas with confidence bands.
- **Zero-Shot Tabular Valuation (`TabFM`)**: Employs foundation tabular regression models to compute fair-value comps and rental yields without custom training pipelines.
- **Open Knowledge Format (OKF) Semantic Grounding**: Grounds AI queries against certified metric dictionaries and underwriting policies.
- **Interactive Cloud Run Web Application**: Features an 8-tab Streamlit dashboard with presenter talk tracks, live SQL inspection, and executive valuation cards.

### [Project 2: Enterprise Data, Database, Analytics, Governance & BI Pipeline](./02_enterprise_data_governance_pipeline)
An end-to-end data platform simulating a high-volume B2B distribution catalog and revenue recognition architecture.
- **Operational Database**: Cloud SQL for PostgreSQL hosting normalized master product catalog and reseller transaction tables.
- **Federated Zero-ETL / ELT**: High-performance near-real-time federation via BigQuery External Connections (`EXTERNAL_QUERY`) materializing governed reporting datasets.
- **Declarative Auto Data Quality (Auto DQ)**: Dataplex DataScans enforcing 10 declarative rules across 5 quality dimensions (`COMPLETENESS`, `UNIQUENESS`, `VALIDITY`, `CONSISTENCY`, `INTEGRITY`) with serverless pushdown compute.
- **Automated Steward Remediation**: Automatically generates SQL queries to isolate rule-failing records into `dq_scan_results`.
- **End-to-End 5-Hop Lineage**: Full metadata and lineage tracking from Cloud SQL through BigQuery, scan results, LookML views, and executive dashboards.
- **Looker Business Intelligence**: LookML semantic layer powering **Dashboard #4** (Executive Revenue & Data Quality Trust KPI) and **Dashboard #5** (Data Quality Scorecard & Steward Drilldown).

---

## 🛠️ Technology & Skill Matrix

```text
├── Cloud Architecture & Infrastructure
│   ├── Google Cloud Platform (GCP)
│   ├── Google Cloud Run (Serverless Containers)
│   ├── Google Cloud Storage (Object Stores)
│   └── Cloud SQL for PostgreSQL (Relational OLTP)
│
├── Data Warehousing & Analytics
│   ├── Google Cloud BigQuery (Standard SQL, Federated Queries, Object Tables)
│   ├── BigQuery AI / ML Functions (AI.GENERATE, TimesFM, TabFM, AI.EVALUATE)
│   └── SQL Performance Tuning (Partitioning, Clustering, BI Engine)
│
├── Data Governance & Lineage
│   ├── Google Cloud Dataplex (Auto Data Quality Scans)
│   ├── Google Cloud Knowledge Catalog (Scorecards, Custom Aspects)
│   └── Dataplex Data Lineage API
│
├── Semantic BI & Modeling
│   ├── Looker Core / LookML
│   └── Executive Dashboarding & Scheduled Alerting
│
└── Application Development & Machine Learning
    ├── Python 3.11+
    ├── Streamlit & Plotly Data Visualization
    ├── Docker Containerization
    └── Open Knowledge Format (OKF)
```

---

## 🏁 Getting Started

### Prerequisites
1. A Google Cloud Platform (GCP) project with billing enabled.
2. Google Cloud SDK (`gcloud`) installed and authenticated:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project <YOUR_PROJECT_ID>
   ```
3. Python 3.11+ installed locally.

### Exploration Workflow
1. Navigate to **[`01_property_ai_valuation_engine`](./01_property_ai_valuation_engine)** to explore the BigQuery AI/ML notebooks or launch the Cloud Run Streamlit application.
2. Navigate to **[`02_enterprise_data_governance_pipeline`](./02_enterprise_data_governance_pipeline)** to review the Cloud SQL seeds, Dataplex Auto DQ YAML specifications, LookML models, and live demo choreography.

---

## 📄 License

This repository is shared for educational, internship portfolio, and technical proof-of-concept demonstration purposes.
