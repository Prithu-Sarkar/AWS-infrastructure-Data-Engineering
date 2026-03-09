# C3 W2 Assignment: Data Lakehouse with AWS Lake Formation & Apache Iceberg

## Architecture
**Medallion Architecture** on AWS: Landing → Curated → Presentation zones in S3

## Key Steps Completed

### 1. Setup
- Granted Lake Formation permissions to Glue role for `curated_zone` and `presentation_zone`

### 2. Landing Zone
- Completed Terraform Glue RDS connection (`JDBC_CONNECTION_URL`, `USERNAME`, `PASSWORD`)
- Deployed via Terraform, ran 2 Glue jobs: `batch_ingress`, `json_ingress`

### 3. Curated Zone
- `add_metadata()`: added `classic_models_mysql` source and `ingest_ts` timestamp
- `enforce_schema()`: handled `IntegerType`, `DoubleType`, `DateType` casting
- `SqlQuery0`: filtered latest ratings by `max(ingest_ts)`
- `SqlQuery1`: joined ratings + products + customers for ML table
- Deployed 3 Glue jobs: `csv_transformation`, `ratings_transformation`, `ratings_to_iceberg`

### 4. Presentation Zone (Athena CTAS - Iceberg format)
- `ratings` — raw ratings table
- `ratings_for_ml` — joined customer/product/ratings data
- `sales_report` — monthly sales totals
- `ratings_per_product` — avg rating + review count per product

## AWS Services Used
- **S3** — Data lake storage
- **AWS Glue** — ETL jobs
- **Lake Formation** — Data governance & permissions
- **Apache Iceberg** — Table format (schema evolution, versioning, ACID)
- **Amazon Athena** — Serverless SQL queries
- **Terraform** — Infrastructure as Code
