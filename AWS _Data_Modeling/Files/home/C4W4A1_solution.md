# C4W4A1 — Capstone Part 1: ETL & Data Modeling (Quick Reference)

## Your CloudFormation Values

| Key | Value |
|-----|-------|
| API Endpoint | `ec2-98-95-80-164.compute-1.amazonaws.com` |
| Postgres Endpoint | `de-c4w4a1-rds.cz8uuym4g1or.us-east-1.rds.amazonaws.com` |
| Redshift Endpoint | `de-c4w4a1-redshift-cluster.covelhouyhyc.us-east-1.redshift.amazonaws.com` |
| Scripts Bucket | `de-c4w4a1-181325975426-us-east-1-scripts` |

---

## Step 1 — Environment Setup

```bash
source scripts/setup.sh
```

---

## Step 2 — Fix API Endpoint in glue.tf

```bash
sed -i 's/<API-ENDPOINT>/ec2-98-95-80-164.compute-1.amazonaws.com/g' \
  ~/project/terraform/modules/extract_job/glue.tf

# Verify
grep "ec2-98-95-80" ~/project/terraform/modules/extract_job/glue.tf
```

---

## Step 3 — Upload Glue Scripts to S3

Run in notebook:
```python
SCRIPTS_BUCKET_NAME = 'de-c4w4a1-181325975426-us-east-1-scripts'
```
```bash
aws s3 cp ./terraform/assets/extract_jobs/de-c4w4a1-api-extract-job.py s3://de-c4w4a1-181325975426-us-east-1-scripts/de-c4w4a1-api-extract-job.py
aws s3 cp ./terraform/assets/extract_jobs/de-c4w4a1-extract-songs-job.py s3://de-c4w4a1-181325975426-us-east-1-scripts/de-c4w4a1-extract-songs-job.py
aws s3 cp ./terraform/assets/transform_jobs/de-c4w4a1-transform-json-job.py s3://de-c4w4a1-181325975426-us-east-1-scripts/de-c4w4a1-transform-json-job.py
aws s3 cp ./terraform/assets/transform_jobs/de-c4w4a1-transform-songs-job.py s3://de-c4w4a1-181325975426-us-east-1-scripts/de-c4w4a1-transform-songs-job.py
```

---

## Step 4 — Terraform (run in order)

```bash
cd ~/project/terraform
terraform init
terraform apply -target=module.extract_job -auto-approve
terraform apply -target=module.transform_job -auto-approve
terraform apply -target=module.serving -auto-approve
```

---

## Step 5 — Run Glue Extract Jobs

```bash
aws glue start-job-run --job-name de-c4w4a1-api-users-extract-job | jq -r '.JobRunId'
aws glue start-job-run --job-name de-c4w4a1-api-sessions-extract-job | jq -r '.JobRunId'
aws glue start-job-run --job-name de-c4w4a1-rds-extract-job | jq -r '.JobRunId'

# Check status (replace <ID> with actual JobRunId)
aws glue get-job-run --job-name de-c4w4a1-api-users-extract-job --run-id <ID> --output text --query "JobRun.JobRunState"
aws glue get-job-run --job-name de-c4w4a1-api-sessions-extract-job --run-id <ID> --output text --query "JobRun.JobRunState"
aws glue get-job-run --job-name de-c4w4a1-rds-extract-job --run-id <ID> --output text --query "JobRun.JobRunState"
```
Wait for all 3 → `SUCCEEDED`

---

## Step 6 — Run Glue Transform Jobs

```bash
aws glue start-job-run --job-name de-c4w4a1-json-transform-job | jq -r '.JobRunId'
aws glue start-job-run --job-name de-c4w4a1-songs-transform-job | jq -r '.JobRunId'

# Check status
aws glue get-job-run --job-name de-c4w4a1-json-transform-job --run-id <ID> --output text --query "JobRun.JobRunState"
aws glue get-job-run --job-name de-c4w4a1-songs-transform-job --run-id <ID> --output text --query "JobRun.JobRunState"
```
Wait for both → `SUCCEEDED`

---

## Step 7 — dbt Setup

```bash
cd ~/project
dbt init dbt_modeling
# Select: 1 (redshift)
# host:     de-c4w4a1-redshift-cluster.covelhouyhyc.us-east-1.redshift.amazonaws.com
# port:     Enter (default 5439)
# user:     defaultuser
# auth:     1 (password)
# password: Defaultuserpwrd1234+
# dbname:   dev
# schema:   deftunes_serving
# threads:  1
```

Fix profiles.yml if needed:
```bash
sed -i 's/host: de-c4w4a1/de-c4w4a1/g' ~/.dbt/profiles.yml
sed -i 's/password: .*/password: Defaultuserpwrd1234+/' ~/.dbt/profiles.yml
sed -i 's/schema: .*/schema: deftunes_serving/' ~/.dbt/profiles.yml
```

Test connection:
```bash
cd dbt_modeling
dbt debug
# Expected: Connection test: [OK connection ok]
```

---

## Step 8 — Notebook Graded Cells (Run in Order)

**First run these setup cells:**
```python
%load_ext sql
```
```python
SCRIPTS_BUCKET_NAME = 'de-c4w4a1-181325975426-us-east-1-scripts'
```
```python
# Postgres connection
RDSDBHOST = 'de-c4w4a1-rds.cz8uuym4g1or.us-east-1.rds.amazonaws.com'
postgres_connection_url = f'postgresql+psycopg2://postgresuser:adminpwrd@{RDSDBHOST}:5432/postgres'
%sql {postgres_connection_url}
```
```python
# Redshift connection  ← MUST run before graded cells
REDSHIFTDBHOST = 'de-c4w4a1-redshift-cluster.covelhouyhyc.us-east-1.redshift.amazonaws.com'
redshift_connection_url = f'postgresql+psycopg2://defaultuser:Defaultuserpwrd1234+@{REDSHIFTDBHOST}:5439/dev'
%sql {redshift_connection_url}
```

**Then run the 5 graded cells (ex01–ex05):**
```python
%sql SHOW SCHEMAS FROM DATABASE dev                        # ex01
%sql SHOW TABLES FROM SCHEMA dev.deftunes_transform        # ex02
%sql select * from deftunes_transform.songs limit 10       # ex03
%sql select * from deftunes_transform.sessions limit 10    # ex04
%sql select * from deftunes_transform.users limit 10       # ex05
```

**Save notebook → Ctrl+S → Submit**
