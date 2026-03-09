# Capstone Project Part 2 — Data Quality & Orchestration
### Course 4 · Week 4 Assignment — DeFtunes Data Pipeline

---

## 📋 Project Overview

This project is the second part of the DeFtunes Capstone, extending the existing data pipeline with **data quality checks**, **workflow orchestration**, **analytical views**, and **data visualization**. DeFtunes is a subscription-based music streaming app that has expanded into digital song purchases, requiring a robust end-to-end data pipeline.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          AWS Cloud                                   │
│                                                                      │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│  │ Data Sources│    │  Landing Zone│    │  Transformation Zone  │  │
│  │             │    │  (S3 Bucket) │    │  (S3 - Iceberg Tables)│  │
│  │ DeFtunes API│───►│  /api/users  │───►│  users table          │  │
│  │ /users      │    │  /api/session│    │  sessions table       │  │
│  │ /sessions   │    │  /rds/songs  │    │  songs table          │  │
│  │             │    └──────────────┘    └──────────┬────────────┘  │
│  │ RDS Postgres│              ▲                     │               │
│  │ songs table │              │                     ▼               │
│  └─────────────┘         AWS Glue              Redshift             │
│                          Extract Jobs          Spectrum +           │
│                          Transform Jobs        Glue Catalog         │
│                          Data Quality          │                    │
│                               │                ▼                    │
│                          Apache Airflow    Redshift DWH             │
│                          Orchestration     (Serving Layer)          │
│                               │            dbt Models               │
│                               │            Star Schema              │
│                               │            BI Views                 │
│                               │                │                    │
│                               └────────────────▼                    │
│                                           Apache Superset            │
│                                           Dashboards                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technology Stack

| Component | Technology |
|---|---|
| Infrastructure as Code | Terraform |
| Extract Jobs | AWS Glue (PySpark) |
| Transform Jobs | AWS Glue (Apache Iceberg) |
| Data Warehouse | Amazon Redshift |
| Data Modeling | dbt (data build tool) |
| Data Quality | AWS Glue Data Quality (DQDL) |
| Orchestration | Apache Airflow |
| Visualization | Apache Superset |
| Storage | Amazon S3 |

---

## 📦 CloudFormation Resources

| Key | Value |
|---|---|
| APIEndpoint | `ec2-34-224-207-61.compute-1.amazonaws.com` |
| DataLakeBucket | `de-c4w4a2-606274144233-us-east-1-data-lake` |
| ScriptsBucket | `de-c4w4a2-606274144233-us-east-1-scripts` |
| DagsBucket | `de-c4w4a2-606274144233-us-east-1-dags` |
| DBTBucket | `de-c4w4a2-606274144233-us-east-1-dbt` |
| RedshiftClusterEndpoint | `de-c4w4a2-redshift-cluster.ccog6lplyzz1.us-east-1.redshift.amazonaws.com` |
| AirflowDNS | `http://ec2-34-224-207-61.compute-1.amazonaws.com:8080` |
| SupersetEndpoint | `http://98.95.82.67:8088` |

---

## Part 2 — Infrastructure Deployment

### Terraform Files Modified

#### `terraform/modules/extract_job/glue.tf`
Placeholders replaced:
- `<API-ENDPOINT>` → `ec2-34-224-207-61.compute-1.amazonaws.com` (lines 64, 94)
- `<INGEST_DATE_YYYY-MM-DD>` → `2020-02-01` (lines 37, 66, 96)

#### `terraform/modules/transform_job/glue.tf`
Placeholders replaced:
- `<INGEST_DATE_YYYY-MM-DD>` → `2020-02-01` (lines 21, 53)

### Terraform Deployment Commands

```bash
source scripts/setup.sh
cd terraform
terraform init
terraform plan
terraform apply -target=module.extract_job
terraform apply -target=module.transform_job
terraform apply -target=module.serving
terraform apply -target=module.data_quality
```

### Resources Deployed (14 total)
- 3 AWS Glue Extract Jobs
- 2 AWS Glue Transform Jobs
- 3 AWS Glue Data Quality Rulesets
- 1 AWS Glue Connection (RDS)
- 1 IAM Role + Policy
- 2 Redshift Schemas
- 1 Glue Catalog Database

---

### Glue Jobs Execution

#### Extract Jobs (ran in parallel)

| Job Name | JobRunID | Status |
|---|---|---|
| `de-c4w4a2-api-users-extract-job` | `jr_106ff4e3...` | ✅ SUCCEEDED |
| `de-c4w4a2-api-sessions-extract-job` | `jr_4e53e0b2...` | ✅ SUCCEEDED |
| `de-c4w4a2-rds-extract-job` | `jr_6fad27e3...` | ✅ SUCCEEDED |

#### Transform Jobs

| Job Name | JobRunID | Status |
|---|---|---|
| `de-c4w4a2-json-transform-job` | `jr_6768022a...` | ✅ SUCCEEDED |
| `de-c4w4a2-songs-transform-job` | `jr_cb7b7645...` | ✅ SUCCEEDED |

---

## Part 3 — Data Quality with AWS Glue

### 3.1 — Data Quality Rule Sets (DQDL)

Three rulesets were configured in `terraform/modules/data_quality/glue.tf`:

#### Songs Ruleset
```
Rules = [
  IsComplete "track_id",
  ColumnLength "track_id" = 18,
  IsComplete "song_id",
  ColumnLength "song_id" = 18,
  IsComplete "artist_id"
]
```

#### Sessions Ruleset
```
Rules = [
  IsComplete "user_id",
  IsComplete "session_id",
  ColumnLength "user_id" = 36,
  ColumnLength "session_id" = 36,
  IsComplete "song_id",
  ColumnValues "price" <= 2
]
```

#### Users Ruleset
```
Rules = [
  IsComplete "user_id",
  Uniqueness "user_id" > 0.95,
  IsComplete "user_lastname",
  IsComplete "user_name",
  IsComplete "user_since"
]
```

---

### 3.2 — dbt BI Views

Created new `bi_views` folder under `dbt_modeling/models/` with the following files:

#### `schema.yml`
```yaml
version: 2
models:
  - name: sales_per_country_vw
    description: "Sales per country view"
    columns:
      - name: session_month
      - name: session_year
      - name: country_code
      - name: total_sales
```

#### `sales_per_artist_vw.sql`
```sql
SELECT
  date_part('year', fs.session_start_time) AS session_year,
  da.artist_name,
  SUM(fs.price) AS total_sales
FROM {{var("target_schema")}}.fact_session fs
LEFT JOIN {{var("target_schema")}}.dim_artists da
  ON fs.artist_id = da.artist_id
GROUP BY 1,2
```

#### `sales_per_country_vw.sql`
```sql
SELECT
  date_part('month', fs.session_start_time) AS session_month,
  date_part('year', fs.session_start_time) AS session_year,
  du.country_code,
  SUM(fs.price) AS total_sales
FROM {{var("target_schema")}}.fact_session fs
LEFT JOIN {{var("target_schema")}}.dim_users du
  ON fs.user_id = du.user_id
GROUP BY 1,2,3
```

#### `dbt_project.yml` models section (updated)
```yaml
models:
  dbt_modeling:
    serving_layer:
      +materialized: table
    bi_views:
      +materialized: view
      +schema: bi_views
```

#### Uploaded to S3
```bash
aws s3 cp dbt_modeling/models/bi_views s3://de-c4w4a2-.../dbt_project/dbt_modeling/models/bi_views --recursive
aws s3 cp dbt_modeling/dbt_project.yml s3://de-c4w4a2-.../dbt_project/dbt_modeling/dbt_project.yml
```

---

## Part 4 — Orchestration with Apache Airflow

### 4.1 — Airflow Access
- URL: `http://ec2-34-224-207-61.compute-1.amazonaws.com:8080`
- Username: `airflow` / Password: `airflow`

---

### 4.2 — Songs Pipeline DAG

**File:** `dags/deftunes_songs_pipeline.py`

**Placeholders replaced:**
- `<DATA-LAKE-BUCKET>` → `de-c4w4a2-606274144233-us-east-1-data-lake`
- `<SCRIPTS-BUCKET>` → `de-c4w4a2-606274144233-us-east-1-scripts`
- `<GLUE-EXECUTION-ROLE>` → `arn:aws:iam::606274144233:role/de-c4w4a2-glue-role`

**DAG Tasks (6 total):**

| Task | Operator | Description |
|---|---|---|
| `start` | EmptyOperator | Pipeline start |
| `extract_songs` | GlueJobOperator | Extract songs from RDS |
| `transform_songs` | GlueJobOperator | Transform songs to Iceberg |
| `songs_data_quality` | GlueDataQualityRuleSetEvaluationRunOperator | Run quality checks |
| `dbt_run` | DockerOperator | Run dbt models |
| `end` | EmptyOperator | Pipeline end |

**Uploaded to S3:**
```bash
aws s3 cp dags/deftunes_songs_pipeline.py s3://de-c4w4a2-.../dags/deftunes_songs_pipeline.py
```

---

### 4.3 — API Pipeline DAG

**File:** `dags/deftunes_api_pipeline.py`

**Placeholders replaced:**
- `<DATA-LAKE-BUCKET>` → `de-c4w4a2-606274144233-us-east-1-data-lake`
- `<SCRIPTS-BUCKET>` → `de-c4w4a2-606274144233-us-east-1-scripts`
- `<API-ENDPOINT>` → `ec2-34-224-207-61.compute-1.amazonaws.com`
- `<GLUE-EXECUTION-ROLE>` → `arn:aws:iam::606274144233:role/de-c4w4a2-glue-role`

**Uploaded to S3:**
```bash
aws s3 cp dags/deftunes_api_pipeline.py s3://de-c4w4a2-.../dags/deftunes_api_pipeline.py
```

### DAG Execution Results

Both DAGs successfully deployed and executed:

| DAG | Status | Backfill |
|---|---|---|
| `deftunes_songs_pipeline_dag` | ✅ Active - All Green | 2 months |
| `deftunes_api_pipeline_dag` | ✅ Active - All Green | 3 months |

---

## Part 5 — Data Visualization with Apache Superset

- **URL:** `http://98.95.82.67:8088`
- **Login:** admin / admin
- Connected Redshift via SQLAlchemy URI
- Created datasets from `deftunes_bi_views` schema
- Built charts from `sales_per_artist_vw` and `sales_per_country_vw`
- Assembled into a dashboard

---

## ✅ Assignment Completion Checklist

- [x] Deployed Terraform infrastructure (14 resources)
- [x] Fixed all placeholder values in Glue TF files
- [x] Ran 3 extract Glue jobs successfully
- [x] Ran 2 transform Glue jobs successfully
- [x] Configured 3 Data Quality rulesets
- [x] Created dbt `bi_views` folder and SQL models
- [x] Updated `dbt_project.yml` with bi_views config
- [x] Uploaded dbt files to S3
- [x] Configured and uploaded Songs pipeline DAG
- [x] Configured and uploaded API pipeline DAG
- [x] Both Airflow DAGs running successfully (all green)
- [x] Connected Apache Superset to Redshift
- [x] Created dashboards from BI views

---

## 🔑 Key Concepts Covered

| Concept | Description |
|---|---|
| **Terraform IaC** | Infrastructure as Code for reproducible AWS deployments |
| **AWS Glue** | Serverless ETL for extract and transform jobs |
| **Apache Iceberg** | Open table format for data lake storage |
| **DQDL** | Data Quality Definition Language for Glue quality checks |
| **dbt** | Data transformation and modeling on Redshift |
| **Apache Airflow** | DAG-based workflow orchestration |
| **Backfilling** | Processing historical data in Airflow DAG runs |
| **Redshift Spectrum** | Query S3 data directly from Redshift |
| **Apache Superset** | Open-source BI and data visualization tool |

---

*Assignment completed on March 3, 2026 | Data Engineering Capstone — Course 4, Week 4*
