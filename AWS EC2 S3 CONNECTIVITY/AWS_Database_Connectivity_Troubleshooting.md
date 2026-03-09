# AWS Database Connectivity Troubleshooting
### Course 2 · Week 1 Assignment — Data Engineering on AWS

---

## 📋 Project Overview

This project involves troubleshooting and resolving real-world connectivity and permission issues encountered when connecting an EC2 instance to an RDS PostgreSQL database on AWS. The assignment simulates a DevOps/Data Engineering scenario where infrastructure misconfiguration prevents database access and data ingestion.

**Skills Demonstrated:**
- AWS VPC & Networking concepts
- EC2 & RDS Security Group configuration
- PostgreSQL database operations via `psql`
- S3 bucket policy management (IAM resource-based policies)
- Python scripting with `boto3` for S3 data download
- SQL table creation and data loading

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                     AWS Cloud                        │
│                                                      │
│  ┌─────────────────────┐   ┌──────────────────────┐ │
│  │  VPC: de-c2w1a1     │   │  VPC: external-vpc   │ │
│  │                     │   │                      │ │
│  │  ┌───────────────┐  │   │  ┌────────────────┐  │ │
│  │  │ EC2 (Bastion) │  │   │  │ EC2 (External) │  │ │
│  │  │ 100.50.136.114│  │   │  │  ❌ Wrong VPC  │  │ │
│  │  └──────┬────────┘  │   │  └────────────────┘  │ │
│  │         │ port 5432 │   └──────────────────────┘ │
│  │  ┌──────▼────────┐  │                            │
│  │  │  RDS Postgres │  │   ┌──────────────────────┐ │
│  │  │ de-c2w1a1-rds │  │   │       S3 Bucket      │ │
│  │  └───────────────┘  │   │  de-c2w1a1-...-data  │ │
│  └─────────────────────┘   └──────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## Part 1 — Fixing Database Connectivity Issues

### Problem
Unable to connect from EC2 to RDS PostgreSQL instance.

### Root Causes Found & Fixed

#### Issue 1: Wrong VPC
The first EC2 instance (`de-c2w1a1-external-bastion-host`) was deployed in a **different VPC** than the RDS instance. Resources in different VPCs cannot communicate by default.

| Resource | VPC |
|---|---|
| `de-c2w1a1-external-bastion-host` | `de-c2w1a1-external-bastion-host-vpc` ❌ |
| `de-c2w1a1-bastion-host` | `de-c2w1a1` ✅ |
| `de-c2w1a1-rds` | `de-c2w1a1` ✅ |

**Fix:** Switch to `de-c2w1a1-bastion-host` which resides in the same VPC as RDS.

---

#### Issue 2: Missing Security Group Inbound Rule
Even after switching to the correct VPC, the RDS Security Group (`sg-041a2dc3664290485`) had **no inbound rule allowing TCP traffic on port 5432** (PostgreSQL's default port).

**Fix:** Added the following inbound rule to the RDS Security Group:

| Field | Value |
|---|---|
| Type | Custom TCP |
| Port Range | 5432 |
| Source | `sg-0bfd9a043ad9746fe` (Bastion Host SG) |

> Using the EC2 Security Group ID as the source (instead of `0.0.0.0/0`) follows the **principle of least privilege** — only the bastion host EC2 instance is allowed to connect.

---

#### Issue 3: Incorrect Password
After fixing the network issues, authentication failed with the initially provided password `postgrespwrd`.

**Fix:** Used the updated password `adminpwrd` provided by the DevOps team after maintenance.

---

### Successful Connection Command

```bash
psql --host=de-c2w1a1-rds.czmos2qq4u3o.us-east-1.rds.amazonaws.com \
     --username=postgres \
     --password \
     --port=5432
```

**Connection Details:**

| Parameter | Value |
|---|---|
| Host | `de-c2w1a1-rds.czmos2qq4u3o.us-east-1.rds.amazonaws.com` |
| Port | `5432` |
| Username | `postgres` |
| SSL | TLSv1.2 (ECDHE-RSA-AES128-GCM-SHA256) |

---

## Part 2 — Fixing Permission Issues

### Objective
Download a CSV dataset from S3 and load it into the RDS PostgreSQL database.

---

### Step 2.1 — Download Lab Files from S3

```bash
aws s3 cp --recursive s3://dlai-data-engineering/labs/c2w1a1-814493-vocapi/ ./
```

Files downloaded:
- `sql/ratings_table_ddl.sql` — DDL script to create the table
- `sql/copy_data.sql` — SQL script to load data
- `scripts/download_from_s3.py` — Python script to download dataset

---

### Step 2.2 — Create the Database Table

Connected to the database and executed the DDL script:

```bash
postgres=> \i sql/ratings_table_ddl.sql
```

**Output:**
```
NOTICE:  table "ratings_training" does not exist, skipping
DROP TABLE
CREATE TABLE
```

The `ratings_training` table was created successfully with the following columns:

| Column | Type |
|---|---|
| city | text |
| state | text |
| postalcode | text |
| country | text |
| creditlimit | numeric |
| productcode | text |
| productline | text |
| productscale | text |
| quantityinstock | integer |
| buyprice | numeric |
| msrp | numeric |
| productrating | integer |
| customernumber | integer |

---

### Step 2.3 — Fix S3 Permission Error

#### Problem
Running the Python download script returned a **403 Forbidden** error:

```
Error downloading file: An error occurred (403) when calling the
HeadObject operation: Forbidden
```

#### Root Cause
The S3 bucket had a **Deny** policy blocking all `GetObject` operations:

```json
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Deny",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::de-c2w1a1-334568913648-us-east-1-data/*"
    }]
}
```

#### Fix — Updated Bucket Policy

Replaced the Deny policy with an **Allow policy** scoped to:
- Only `s3:GetObject` action
- Only the `/csv/` folder
- Only from the EC2 bastion host's public IP (`100.50.136.114`)

```json
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::de-c2w1a1-334568913648-us-east-1-data/csv/*",
        "Condition": {
            "IpAddress": {
                "aws:SourceIp": "100.50.136.114"
            }
        }
    }]
}
```

---

### Step 2.4 — Download Dataset & Load into Database

After fixing the bucket policy:

```bash
# Create data directory
mkdir -p data

# Run download script
python3 scripts/download_from_s3.py
# Output: File downloaded successfully to data/ratings_ml_training_dataset.csv

# Connect to DB and load data
postgres=> \i sql/copy_data.sql
# Output: COPY 2532
```

✅ **2,532 rows** successfully loaded into `ratings_training` table.

---

### Step 2.5 — Verify Data

```sql
SELECT * FROM ratings_training LIMIT 10;
```

Sample output:

| city | country | productline | productrating |
|---|---|---|---|
| London | UK | Classic Cars | 5 |
| Nantes | France | Classic Cars | 2 |
| Montréal | Canada | Trucks and Buses | 2 |
| Nantes | France | Motorcycles | 4 |

---

## 🔑 Key AWS Concepts Covered

| Concept | Description |
|---|---|
| **VPC** | Virtual Private Cloud — isolated network environment on AWS |
| **Security Groups** | Virtual firewall controlling inbound/outbound traffic for AWS resources |
| **Inbound Rules** | Rules that define what traffic is allowed INTO a resource |
| **Least Privilege** | Security best practice — grant only the minimum permissions needed |
| **Resource-based Policy** | S3 bucket policy controlling who can access the bucket and how |
| **IP Condition** | Restricts S3 access to requests originating from a specific IP address |

---

## 📁 Project Files

```
project/
├── sql/
│   ├── ratings_table_ddl.sql    # Creates ratings_training table
│   └── copy_data.sql            # Loads CSV data into table
└── scripts/
    └── download_from_s3.py      # Downloads dataset from S3 using boto3
```

---

## ✅ Assignment Completion Checklist

- [x] Connected to AWS Console
- [x] Identified RDS endpoint
- [x] Diagnosed VPC mismatch issue
- [x] Switched to correct EC2 bastion host
- [x] Added Security Group inbound rule for port 5432
- [x] Fixed authentication with correct password
- [x] Downloaded lab files from S3
- [x] Created `ratings_training` table in PostgreSQL
- [x] Diagnosed and fixed S3 403 Forbidden error
- [x] Applied least-privilege S3 bucket policy
- [x] Downloaded dataset using Python/boto3
- [x] Loaded 2,532 rows into RDS database
- [x] Verified data with SQL query

---

*Assignment completed on March 3, 2026 | AWS Data Engineering — Course 2, Week 1*
