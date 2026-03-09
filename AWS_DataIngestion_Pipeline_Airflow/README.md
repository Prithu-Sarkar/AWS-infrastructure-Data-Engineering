# C2W4 Assignment: Building an Advanced Data Pipeline With Data Quality Checks

## Project Description

This project implements an **Apache Airflow ML pipeline** for three fictitious Mobility-As-A-Service (MaaS) vendors:
- **Easy Destiny**
- **Alitran**
- **To My Place AI**

The pipeline validates data quality, trains a Linear Regression model to estimate ride duration, evaluates performance, and decides whether to deploy or notify based on RMSE score.

---

## What Was Built

### Pipeline Tasks (DAG)
The DAG consists of the following tasks in order:

```
start → data_quality → train_and_evaluate → is_deployable → deploy / notify → end
```

| Task | Description |
|------|-------------|
| `start` | Empty DummyOperator marking DAG start |
| `data_quality` | GXValidateDataFrameOperator — checks `passenger_count` is between 1 and 6 |
| `train_and_evaluate` | Trains Linear Regression, returns RMSE on test data |
| `is_deployable` | BranchPythonOperator — deploys if RMSE < 500, else notifies |
| `deploy` | Prints deployment message |
| `notify` | Prints notification message to vendor admin email |
| `end` | DummyOperator with `trigger_rule="none_failed_or_skipped"` |

### Dynamic DAGs
Used Jinja2 templating to generate 3 identical DAGs (one per vendor) from a single `template.py` and 3 JSON config files — following the DRY principle.

---

## Expected Results

| DAG | Expected Outcome |
|-----|-----------------|
| `model_trip_duration_easy_destiny` | ✅ Deploys (RMSE < 500) |
| `model_trip_duration_alitran` | ⚠️ Notifies (RMSE ≥ 500) |
| `model_trip_duration_to_my_place_ai` | ❌ Fails at data_quality (passenger_count > 6) |

---

## File Structure

```
project/
├── src/
│   ├── model_trip_duration_easy_destiny.py   ← Completed DAG (Exercises 1–4)
│   ├── templates/
│   │   ├── template.py                        ← Jinja2 DAG template
│   │   ├── generate_dags.py                   ← Script to generate DAGs
│   │   └── dag_configs/
│   │       ├── config_easy_destiny.json
│   │       ├── config_alitran.json
│   │       └── config_to_my_place_ai.json
│   └── dags/                                  ← Generated DAGs (upload to S3)
│       ├── model_trip_duration_easy_destiny.py
│       ├── model_trip_duration_alitran.py
│       └── model_trip_duration_to_my_place_ai.py
└── data/
    └── work_zone/
        └── data_science_project/
            └── datasets/
                ├── easy_destiny/
                ├── alitran/
                └── to_my_place_ai/
```

---

## How to Run (Coursera Environment)

### 1. Upload data to S3
```bash
cd data
aws s3 sync work_zone s3://<RAW-DATA-BUCKET>/work_zone/
cd ..
```

### 2. Generate Dynamic DAGs
```bash
cd src/templates
python3 ./generate_dags.py
cd ../..
```

### 3. Upload DAGs to S3
```bash
aws s3 sync src/dags s3://<DAGS-BUCKET>/dags
```

### 4. Set Airflow Variable
In Airflow UI → Admin → Variables → Add:
- Key: `bucket_name`
- Val: `<RAW-DATA-BUCKET>`

### 5. Trigger DAGs
In Airflow UI, toggle each DAG on one at a time and monitor results.

---

## Technologies Used

- **Apache Airflow** — Pipeline orchestration
- **Great Expectations** — Data quality validation
- **Jinja2** — Dynamic DAG templating
- **pandas** — Data loading
- **scipy** — Linear regression model
- **numpy** — RMSE calculation
- **AWS S3** — Data and DAG storage
