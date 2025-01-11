# Final Project: Data Warehouse & Business Intelligence

**Implementation of Modern Data Warehouse Architecture Using Apache Ecosystem**

## General Description
PT DWBI Sejahtera, an electronics company in Indonesia, plans to expand its market internationally. By analyzing currency fluctuations and sales projections, the company leverages a modern data warehouse concept to support its business strategy.

## Data Source
- **Internal Sales Data:** Sales data from PT DWBI.
- **External Data:** Currency exchange rate streaming API from [OpenExchangeRates](https://openexchangerates.org/).

## Tools Used
- **KNIME:** ETL for data extraction, transformation, and loading.
- **Docker:** Containerization for testing environments and deployment.
- **Visual Studio Code:** Code writing and integration with big data tools.
- **Apache NiFi:** Automation of real-time data integration.
- **Apache Spark:** Big data processing (batch & real-time).
- **Hadoop (HDFS):** Distributed data storage.
- **Apache Hive:** SQL-like queries for data analysis.
- **Apache Superset:** Interactive data visualization.

## Implementation of Modern Data Warehouse Architecture
### Key Stages:
1. **Ingestion**
   - **Batch Data:** Validation and processing using Apache NiFi.
   - **Stream Data:** Real-time USD-Rupiah exchange rates via Apache Spark.
2. **Data Storage**
   - HDFS for batch and real-time data.
3. **Preparation & Training**
   - Data cleansing and revenue prediction model training using Spark MLlib.
4. **Modeling & Serving Data**
   - Querying and data optimization using Apache Hive.
5. **Visualization**
   - Interactive dashboards created with Apache Superset.

## Data Warehouse Architecture
For a detailed reference to the architecture implemented in this project, please refer to the [Datawarehouse Architecture.pdf](./Datawarehouse%20Architecture.pdf) document included in this directory.

## Final Results
- **Total Sales:** Rp38.6M (425K orders).
- **Top Vendor by Sales:** Advan (20.44%).
- **Best-Selling Product:** Sharp Aquos SH-C06 SMARTPHONE (Rp1.83M).
- **Sales Prediction:** Historical USD-Rupiah exchange rate data used for projections.
