# Data Transformations with Apache Spark on AWS EMR
### Course 4 — Week 3 Assignment | Data Engineering

---

## Project Overview

This project demonstrates end-to-end data transformation using **Apache Spark** on **AWS EMR (Elastic MapReduce)**. The objective was to extract data from a relational PostgreSQL database (Amazon RDS), transform it into a **Star Schema** data warehouse model, and load the results back into the database — following the classic **ETL (Extract, Transform, Load)** pipeline pattern.

---

## Architecture

```
Amazon RDS (PostgreSQL)
        │
        ▼
  Apache Spark (EMR Cluster)
  ┌─────────────────────────┐
  │  PySpark Transformations │
  │  - SQL Queries           │
  │  - Surrogate Keys (UDF)  │
  │  - Joins & Aggregations  │
  └─────────────────────────┘
        │
        ▼
classicmodels_star_schema (PostgreSQL)
  ├── dim_customers
  ├── dim_products
  ├── dim_offices
  ├── dim_employees
  ├── dim_date
  └── fact_orders
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Apache Spark (PySpark)** | Distributed data processing & transformations |
| **AWS EMR** | Managed Spark cluster execution environment |
| **AWS EMR Studio** | Jupyter-based notebook interface for EMR |
| **Amazon RDS (PostgreSQL)** | Source and target relational database |
| **Amazon S3** | Notebook storage and submission |
| **AWS CloudShell** | CLI operations and S3 file management |
| **JDBC (PostgreSQL Driver)** | Database connectivity from Spark |

---

## Dataset

The source database used was the **ClassicModels** dataset — a sample database representing a retailer of scale model cars. It contains the following source tables:

- `customers` — Customer details and credit limits
- `employees` — Sales representatives and job titles
- `offices` — Office locations by region
- `products` — Product catalog with pricing
- `productlines` — Product category descriptions
- `orders` — Customer orders with dates
- `orderdetails` — Line items per order with quantities and prices

---

## Environment Setup

### 1. EMR Studio Configuration
- Created an **EMR Studio** workspace (`de-c4w3a1-studio-workspace`) within the pre-provisioned studio `de-c4w3a1-studio-emr`
- Attached the workspace to a running EMR cluster (`de-c4w3a1-cluster`) in **Waiting** state
- Launched the workspace in **Jupyter** mode

### 2. Spark Session Configuration
```python
%%configure -f
{
    "conf": {
        "spark.pyspark.python": "python",
        "spark.pyspark.virtualenv.enabled": "true",
        "spark.pyspark.virtualenv.type": "native",
        "spark.pyspark.virtualenv.bin.path": "/usr/bin/virtualenv",
        "spark.jars.packages": "org.postgresql:postgresql:42.2.5"
    }
}
```

### 3. Database Connection
```python
RDS_ENDPOINT = "de-c4w3a1-rds.cv6sy0w0s62w.us-east-1.rds.amazonaws.com"
jdbc_url = f"jdbc:postgresql://{RDS_ENDPOINT}:5432/postgres"
jdbc_properties = {
    "user": "postgresuser",
    "password": "adminpwrd",
    "driver": "org.postgresql.Driver"
}
```

---

## Data Transformations

### Surrogate Key Generation
A custom **UDF (User Defined Function)** was implemented to generate surrogate keys using MD5 hashing, ensuring consistent and unique keys across all dimension tables:

```python
from pyspark.sql.functions import udf, col, array
from pyspark.sql.types import StringType
import hashlib

def surrogateKey(values):
    combined = "_".join([str(v) for v in values])
    return hashlib.md5(combined.encode()).hexdigest()

surrogateUDF = udf(surrogateKey, StringType())
```

---

### Dimension Tables

#### `dim_customers`
Extracted customer details with surrogate key generated from `customerNumber`:
```sql
SELECT 
    CAST(customerNumber as string) as customer_number, 
    customerName as customer_name,
    CONCAT(contactFirstName, ' ', contactLastName) as contact_name, 
    phone, addressLine1 as address_line_1, addressLine2 as address_line_2, 
    postalCode as postal_code, city, state, country, creditLimit as credit_limit
FROM customers
```

#### `dim_products`
Joined `products` with `productlines` to include product line descriptions:
```sql
SELECT 
    CAST(productCode as string) as product_code, 
    productName as product_name, products.productLine as product_line, 
    productScale as product_scale, productVendor as product_vendor,
    productDescription as product_description, 
    textDescription as product_line_description
FROM products
JOIN productlines ON products.productLine = productlines.productLine
```

#### `dim_offices`
Extracted office location data with surrogate key from `officeCode`.

#### `dim_employees`
Extracted employee details with surrogate key from `employeeNumber`.

#### `dim_date`
Generated a complete date dimension spanning **2003–2005** with the following attributes:
- Day of week, month, year
- Week of year, day of year
- Month name, quarter of year

```python
def get_quarter_of_year(date):
    return (date.month - 1) // 3 + 1

date_dim_df = date_range_df\
    .withColumn("day_of_week", dayofweek("date_day"))\
    .withColumn("day_of_month", dayofmonth("date_day"))\
    .withColumn("day_of_year", dayofyear("date_day"))\
    .withColumn("week_of_year", weekofyear("date_day"))\
    .withColumn("month_of_year", month("date_day"))\
    .withColumn("year", year("date_day"))\
    .withColumn("month_name", date_format("date_day", "MMMM"))\
    .withColumn("quarter_of_year", get_quarter_of_year_udf("date_day"))
```

---

### Fact Table

#### `fact_orders`
The central fact table was built by joining all relevant source tables and computing key metrics:

| Column | Description |
|---|---|
| `fact_order_key` | Surrogate key from orderNumber + lineNumber |
| `customer_key` | FK to dim_customers |
| `employee_key` | FK to dim_employees |
| `office_key` | FK to dim_offices |
| `product_key` | FK to dim_products |
| `order_date` | Date of order |
| `quantity_ordered` | Units ordered |
| `product_price` | Price per unit |
| `profit` | Price - Buy Price |
| `discount_percentage` | (MSRP - Price) / MSRP × 100 |

```sql
SELECT 
    orders.orderNumber, 
    cast(orderdetails.orderLineNumber as string) as order_line_number,
    cast(orders.customerNumber as string) as customer_number, 
    cast(employees.employeeNumber as string) as employee_number,
    offices.officeCode, orderdetails.productCode, 
    orders.orderDate as order_date,
    orders.requiredDate as order_required_date, 
    orders.shippedDate as order_shipped_date,
    orderdetails.quantityOrdered as quantity_ordered, 
    orderdetails.priceEach as product_price,
    (orderdetails.priceEach - products.buyPrice) as profit,
    (products.msrp - orderdetails.priceEach)/products.msrp * 100 as discount_percentage
FROM orders
JOIN orderdetails ON orders.orderNumber = orderdetails.orderNumber
JOIN customers ON orders.customerNumber = customers.customerNumber
JOIN employees ON customers.salesRepEmployeeNumber = employees.employeeNumber
JOIN offices ON employees.officeCode = offices.officeCode
JOIN products ON products.productCode = orderdetails.productCode
```

---

## Star Schema Output

All transformed tables were written back to the `classicmodels_star_schema` schema in PostgreSQL using Spark's JDBC writer in **overwrite** mode:

```python
df.write.jdbc(
    url=jdbc_url, 
    table="classicmodels_star_schema.table_name", 
    mode="overwrite", 
    properties=jdbc_properties
)
```

---

## Key Learnings

- Configured and launched a **PySpark kernel** in AWS EMR Studio connected to a live EMR cluster
- Used **JDBC connectors** to read from and write to a PostgreSQL RDS instance via Spark
- Built **dimension and fact tables** following Star Schema design principles
- Implemented **custom UDFs** for surrogate key generation using MD5 hashing
- Used **Spark SQL** for complex multi-table joins and column transformations
- Generated a **date dimension table** programmatically using Spark sequence functions

---

## Submission

The completed notebook was submitted to the grading S3 bucket using AWS CLI:

```bash
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3 cp s3://de-c4w3a1-$ACCOUNT_ID-us-east-1-emr-bucket/emr-studio/.../C4_W3_Assignment.ipynb \
    s3://de-c4w3a1-$ACCOUNT_ID-us-east-1-submission/C4_W3_Assignment_Learner.ipynb
```

**Submission confirmed:** `C4_W3_Assignment_Learner.ipynb` (99,357 bytes) — March 05, 2026

---

*Course 4, Week 3 — Data Engineering Specialization*
