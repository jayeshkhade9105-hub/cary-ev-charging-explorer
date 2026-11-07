# ⚡ Cary EV Charging Explorer

An end-to-end spatial data engineering pipeline and interactive map application built with **AWS S3 Express One Zone**, **AWS Lambda**, **Amazon Location Service**, **AWS Glue Data Catalog**, **Amazon Athena (Apache Iceberg)**, and **Leaflet.js**.

Visualizes public EV charging session records from the Town of Cary, NC.

---

## 🏗️ AWS Data Pipeline Architecture
[Raw JSON Dataset]

        │
        ▼         
[Amazon S3 Express One Zone] (Staging Directory Bucket)

        │
        ▼
[AWS Lambda + Amazon Location Service] (Serverless ETL & Geocoding)

        │
        ▼
[Amazon S3 Standard] (Clean CSV Storage)

        │
        ▼
[AWS Glue Data Catalog + Amazon Athena] (Apache Iceberg Open Table Format)

        │
        ▼
[Leaflet.js + Esri Basemaps] (Interactive Client Map)

### Stack & Components

* **Amazon S3 Express One Zone (`cary-ev-stations--apse2-az1--x-s3`):** Staging bucket for high-frequency, single-digit millisecond latency reads of municipal JSON uploads.
* **AWS Lambda (`geocode-ev-stations`):** Serverless Python function that parses JSON arrays, handles spatial coordinate fallbacks, and outputs a clean CSV stream directly to S3 Standard in under 2 seconds.
* **Amazon Location Service (`ev-place-index`):** Place index for address geocoding fallback resolution.
* **AWS Glue Data Catalog (`ev_charging_db`):** Central metadata management for raw staging tables (`ev_stations_raw_csv`) and production tables.
* **Amazon Athena & Apache Iceberg (`charging_stations`):** SQL query engine running over open-table Apache Iceberg format stored on S3 Standard (`cary-ev-stations-standard-jayesh`).
* **Frontend Web Application (`ev.html`):** Leaflet.js dashboard using Esri raster basemaps and MarkerCluster for smooth browser rendering.

---

## 🛠️ Repository Structure
├── lambda_function.py    # Python AWS Lambda ETL script

├── ev.html               # Interactive Leaflet web map frontend

└── README.md             # Project documentation

---

## 🚀 Getting Started

### 1. Prerequisites
* AWS Account with active S3, Lambda, Athena, and Glue permissions.
* Python 3.x (for Lambda development).

### 2. AWS Setup
1. Upload `electric-vehicle-charging-stations.json` to your S3 Express directory bucket.
2. Deploy `lambda_function.py` to AWS Lambda and configure your target S3 Standard output bucket.
3. In Amazon Athena, run the DDL schema creation and populate your Iceberg table:

```sql
-- Create production Iceberg table
CREATE TABLE ev_charging_db.charging_stations (
  station_name string,
  street_address string,
  longitude double,
  latitude double,
  kwh_consumed double,
  charging_duration_minutes int
)
LOCATION 's3://cary-ev-stations-standard-jayesh/iceberg-table/'
TBLPROPERTIES ('table_type'='ICEBERG');


