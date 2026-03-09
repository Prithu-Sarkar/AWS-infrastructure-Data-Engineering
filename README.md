# ☁️ AWS Cloud & Data Engineering Portfolio

> **Prithu Sarkar** | MLOps & Data Engineering | IIT Guwahati  
> Hands-on portfolio of real-world AWS data engineering projects covering ingestion, transformation, modeling, quality, and orchestration.

[![AWS](https://img.shields.io/badge/AWS-Cloud-orange?logo=amazon-aws)](https://aws.amazon.com/)
[![Apache Spark](https://img.shields.io/badge/Apache-Spark-red?logo=apachespark)](https://spark.apache.org/)
[![Airflow](https://img.shields.io/badge/Apache-Airflow-blue?logo=apacheairflow)](https://airflow.apache.org/)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-purple?logo=terraform)](https://terraform.io/)

---

## 📁 Project Index

| # | Project | Key Technologies | Focus Area |
|---|---------|-----------------|------------|
| 1 | [AWS EC2 S3 Connectivity](#1-aws-ec2--s3-connectivity) | EC2, S3, RDS, PostgreSQL | Cloud Infra & Networking |
| 2 | [AWS DataLake Apache Iceberg](#2-aws-datalake--apache-iceberg) | S3, Iceberg, Glue | Data Lake Architecture |
| 3 | [Apache Spark on AWS EMR](#3-apache-spark-on-aws-emr) | EMR, PySpark, S3 | Big Data Transformation |
| 4 | [AWS Neo4j Graph DB](#4-aws-neo4j-graph-database) | Neo4j, Cypher, AWS | Graph Data Modeling |
| 5 | [AWS Data Modeling with dbt](#5-aws-data-modeling-with-dbt) | dbt, Redshift, SQL | Data Warehouse Modeling |
| 6 | [AWS DataIngestion Pipeline Airflow](#6-aws-data-ingestion-pipeline--airflow) | Airflow, DAGs, Python | Pipeline Orchestration |
| 7 | [AWS Data Processing API](#7-aws-data-processing-api) | Python, REST API, S3 | API Data Processing |
| 8 | [AWS Data Quality — Great Expectations](#8-aws-data-quality--great-expectations) | Great Expectations, PostgreSQL | Data Quality & Validation |
| 9 | [AWS Glue + Redshift + Terraform](#9-aws-glue--redshift--terraform) | Glue, Redshift, Terraform, S3 | ETL & IaC |
| 10 | [SQL Star Schema](#10-sql-star-schema) | SQL, Star Schema, DWH | Data Warehouse Design |

---

## 1. AWS EC2 & S3 Connectivity

**Goal:** Establish secure connectivity between EC2, S3, and RDS PostgreSQL in a cloud environment.

**What I did:**
- Launched and configured EC2 instances with appropriate Security Groups and Inbound Rules
- Connected EC2 to an RDS PostgreSQL instance and ran DDL/DML scripts
- Loaded data from S3 into PostgreSQL using `COPY` commands via Python scripts
- Configured IAM roles and network settings for secure cross-service communication

**Tech Stack:** `EC2` `S3` `RDS` `PostgreSQL` `Python` `SQL`

**Key Skills:** VPC networking, Security Groups, IAM, EC2-RDS connectivity, S3 data loading

---

## 2. AWS DataLake & Apache Iceberg

**Goal:** Build a modern data lake on AWS using the Apache Iceberg table format for ACID-compliant analytics.

**What I did:**
- Designed and implemented a data lake architecture on S3 using Apache Iceberg
- Leveraged Iceberg features: **Schema Evolution, Time Travel, Hidden Partitioning, Snapshots**
- Managed table metadata, manifests, and row-level deletes
- Queried Iceberg tables with full ACID transaction support

**Tech Stack:** `S3` `Apache Iceberg` `AWS Glue` `PySpark` `Python`

**Key Skills:** Data lake design, Iceberg table format, schema evolution, time travel queries, partitioning strategies

---

## 3. Apache Spark on AWS EMR

**Goal:** Perform large-scale distributed data transformations using Apache Spark on AWS EMR.

**What I did:**
- Spun up and configured an AWS EMR cluster for distributed computing
- Wrote PySpark jobs for data transformation, aggregation, and enrichment
- Read from and wrote back to S3 in optimized formats (Parquet)
- Tuned Spark configurations for performance optimization

**Tech Stack:** `AWS EMR` `Apache Spark` `PySpark` `S3` `Parquet`

**Key Skills:** Distributed computing, Spark transformations, EMR cluster management, S3 I/O optimization

---

## 4. AWS Neo4j Graph Database

**Goal:** Model and query connected data using Neo4j graph database deployed on AWS.

**What I did:**
- Modeled data as nodes and relationships in a property graph
- Wrote Cypher queries for traversal, pattern matching, and aggregation
- Loaded data from AWS into Neo4j and ran analytical queries
- Explored graph-based recommendations and relationship analysis

**Tech Stack:** `Neo4j` `Cypher` `AWS` `Python`

**Key Skills:** Graph data modeling, Cypher querying, node/relationship design, graph analytics

---

## 5. AWS Data Modeling with dbt

**Goal:** Build a structured, testable data warehouse using dbt on AWS Redshift.

**What I did:**
- Designed dimensional models (facts and dimensions) using dbt
- Wrote modular SQL models with `ref()` and `source()` functions
- Configured `dbt_project.yml`, profiles, and schema settings
- Applied dbt tests for data quality and documentation generation

**Tech Stack:** `dbt` `AWS Redshift` `SQL` `Python` `YAML`

**Key Skills:** Data modeling, dbt transformations, dimensional modeling, SQL testing, analytics engineering

---

## 6. AWS Data Ingestion Pipeline — Airflow

**Goal:** Design and orchestrate multi-tenant data ingestion pipelines using Apache Airflow.

**What I did:**
- Built dynamic DAGs using a template-based approach (`template.py`, `generate_dags.py`)
- Created separate ingestion pipelines for multiple clients (alitran, easy_destiny, to_my_place_ai)
- Used JSON config files to parameterize DAG behavior per tenant
- Modeled trip duration prediction workflows as Airflow DAGs with operators and sensors

**Tech Stack:** `Apache Airflow` `Python` `DAGs` `JSON Config` `AWS`

**Key Skills:** DAG design, dynamic DAG generation, multi-tenant pipeline architecture, Airflow operators & sensors

---

## 7. AWS Data Processing API

**Goal:** Build a data processing pipeline that integrates with a REST API (Spotify-style) to ingest and process music data.

**What I did:**
- Built authentication and endpoint modules for API access
- Handled OAuth token management and API response parsing
- Processed JSON responses (albums, tracks, releases) into structured data
- Mocked Spotify API responses for testing with `mock_spotify` module

**Tech Stack:** `Python` `REST API` `OAuth` `JSON` `AWS S3`

**Key Skills:** API authentication, REST data ingestion, response parsing, mock testing, data pipeline design

---

## 8. AWS Data Quality — Great Expectations

**Goal:** Implement automated data quality validation using Great Expectations on AWS.

**What I did:**
- Configured a Great Expectations (GX) project with Data Sources and Expectation Suites
- Defined expectations on taxi trip data (schema, nulls, ranges, uniqueness)
- Generated and reviewed **Data Docs** — HTML validation reports
- Ran validation checkpoints and analyzed pass/fail results
- Managed uncommitted config variables and GX store backends

**Tech Stack:** `Great Expectations` `PostgreSQL` `Python` `AWS` `HTML Data Docs`

**Key Skills:** Data quality framework setup, expectation authoring, validation pipelines, data observability

---

## 9. AWS Glue + Redshift + Terraform

**Goal:** Build a fully automated ETL pipeline using AWS Glue, Redshift, and Terraform for infrastructure provisioning.

**What I did:**
- Provisioned AWS infrastructure (Glue, Redshift, S3) using **Terraform (IaC)**
- Built Glue ETL jobs to extract, transform, and load data into Redshift
- Configured Glue Data Catalog for metadata management
- Automated end-to-end pipeline deployment via Terraform scripts

**Tech Stack:** `AWS Glue` `Amazon Redshift` `Terraform` `S3` `Python`

**Key Skills:** Infrastructure as Code, ETL pipeline design, Glue job authoring, Redshift loading, cloud automation

---

## 10. SQL Star Schema

**Goal:** Design and implement a Star Schema data warehouse for analytical querying.

**What I did:**
- Designed fact and dimension tables following the Star Schema pattern
- Wrote SQL DDL scripts for schema creation and data population
- Optimized queries for analytical workloads using joins across fact/dimension tables
- Applied normalization and denormalization principles for performance

**Tech Stack:** `SQL` `Star Schema` `Data Warehouse` `PostgreSQL`

**Key Skills:** Dimensional modeling, fact/dimension table design, SQL DDL/DML, analytical query optimization

---

## 🛠️ Full Tech Stack

### Cloud & Infrastructure
`AWS EC2` `AWS S3` `AWS RDS` `AWS EMR` `AWS Glue` `AWS Redshift` `Amazon CloudFront` `AWS IAM` `Terraform`

### Data Engineering
`Apache Spark` `Apache Airflow` `Apache Iceberg` `Apache Kafka` `dbt` `Great Expectations`

### Databases & Storage
`PostgreSQL` `Amazon Redshift` `Neo4j` `S3 Data Lake` `Parquet` `JSON` `Avro`

### Programming
`Python` `PySpark` `SQL` `Cypher` `YAML` `Bash`

### DevOps & Tooling
`Docker` `Kubernetes` `Terraform` `Git` `Jupyter Notebooks` `VS Code`

---

## 📊 Skills Summary

```
Cloud Infrastructure     ████████████████████  AWS (EC2, S3, EMR, Glue, Redshift)
Data Pipelines           ████████████████████  Airflow, Spark, Glue ETL
Data Lake / Lakehouse    ███████████████░░░░░  Iceberg, S3, Parquet
Data Modeling            ████████████████░░░░  dbt, Star Schema, Dimensional Modeling
Data Quality             ███████████████░░░░░  Great Expectations, Validation Pipelines
Graph Databases          ████████████░░░░░░░░  Neo4j, Cypher
Infrastructure as Code   ████████████░░░░░░░░  Terraform
API Integration          ████████████░░░░░░░░  REST APIs, OAuth, JSON Processing
```

---

## 🎓 Education & Context

MLOps Specialization**  
Projects completed as part of a structured MLOps and Data Engineering curriculum covering the full modern data stack on AWS.

---

*Portfolio actively maintained and updated as new projects are completed.*  
🔗 [GitHub Repository](https://github.com/Prithu-Sarkar/AWS-infrastructure-Data-Engineering)
