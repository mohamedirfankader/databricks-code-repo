# Databricks notebook source
# MAGIC %md
# MAGIC ###Usecase2: Telecom data - CDC, CDF, SCD

# COMMAND ----------

# MAGIC %md
# MAGIC ![](devices_cdc1.png)

# COMMAND ----------

# MAGIC %md
# MAGIC **Prerequisites - One time activity (done by admin, based on the request)**
# MAGIC
# MAGIC STEP 1: CREATE CONNECTION (FOREIGN CATALOG)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE CONNECTION telecom_gcp_mysql_conn2
# MAGIC TYPE MYSQL
# MAGIC OPTIONS (
# MAGIC   host '35.223.80.16',
# MAGIC   port '3306',
# MAGIC   user 'inceptez',
# MAGIC   password 'Inceptez@123');

# COMMAND ----------

# MAGIC %md
# MAGIC STEP 2: CREATE FOREIGN CATALOG

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE FOREIGN CATALOG telecom_federated_wd36_fc
# MAGIC USING CONNECTION telecom_gcp_mysql_conn2;

# COMMAND ----------

# MAGIC %md
# MAGIC STEP 3: VERIFY SOURCE TABLE (LIVE QUERY)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM telecom_federated_wd36_fc.telecom_devices.device_master;

# COMMAND ----------

# MAGIC %md
# MAGIC STEP 4: CREATE LAYERS (BRONZE / SILVER / GOLD)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS telecom_bronze;
# MAGIC CREATE SCHEMA IF NOT EXISTS telecom_silver;
# MAGIC CREATE SCHEMA IF NOT EXISTS telecom_gold;

# COMMAND ----------

# MAGIC %md
# MAGIC **Interview Questions wrt CDC, CDF, SCD1 & SCD2**
# MAGIC
# MAGIC Change Data Feed (CDF)
# MAGIC
# MAGIC Question: Why use Change Data Feed (CDF)?
# MAGIC
# MAGIC Answer: It saves time and compute costs by only processing the rows that actually changed, instead of scanning the entire table.
# MAGIC
# MAGIC Question: What does CDF output when a row is updated?
# MAGIC
# MAGIC Answer: Two rows: the old version (pre-image) and the new version (post-image).
# MAGIC
# MAGIC Slowly Changing Dimension Type 1 (SCD1)
# MAGIC
# MAGIC Question: What is SCD Type 1?
# MAGIC
# MAGIC Answer: It stores only the latest data. When a change happens, the old data is simply overwritten and lost.
# MAGIC
# MAGIC Question: When should you use SCD Type 1?
# MAGIC
# MAGIC Answer: When you only care about the current status and don't need to track historical changes (e.g., fixing a typo).
# MAGIC
# MAGIC Slowly Changing Dimension Type 2 (SCD2)
# MAGIC
# MAGIC Question: What is SCD Type 2?
# MAGIC
# MAGIC Answer: It keeps the full history of changes. Instead of overwriting, it adds a new row for every update and uses tracking columns (like start/end dates) to show the timeline.
# MAGIC
# MAGIC Question: How do you handle a "delete" in SCD Type 2?
# MAGIC
# MAGIC Answer: You don't actually delete the row. You do a "soft delete" by marking the record as inactive and stamping an end date.

# COMMAND ----------

# MAGIC %md
# MAGIC ###Bronze Layer Load
# MAGIC STEP 5: HISTORICAL/INITIAL LOAD (FIRST TIME INGESTION)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS telecom_bronze.bronze_device_master2 (
# MAGIC   device_id INT, device_type STRING, brand STRING, model STRING, os STRING, 
# MAGIC   owner_customer_id INT, status STRING, updated_at TIMESTAMP
# MAGIC );
# MAGIC
# MAGIC --INSERT INTO telecom_bronze.bronze_device_master2
# MAGIC SELECT device_id, device_type, brand, model, os, owner_customer_id, status, updated_at 
# MAGIC FROM telecom_federated_wd36_fc.telecom_devices.device_master;

# COMMAND ----------

# MAGIC %md
# MAGIC STEP 6: INCREMENTAL CDC LOAD (RUN MULTIPLE TIMES)

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from telecom_bronze.bronze_device_master2

# COMMAND ----------

# MAGIC %sql
# MAGIC --Change Data Capture or Incremental Data ingestion feature using ???
# MAGIC INSERT INTO telecom_bronze.bronze_device_master2
# MAGIC SELECT 
# MAGIC     device_id, 
# MAGIC     device_type, 
# MAGIC     brand, 
# MAGIC     model, 
# MAGIC     os, 
# MAGIC     owner_customer_id, 
# MAGIC     status, 
# MAGIC     updated_at
# MAGIC FROM telecom_federated1.telecom_devices.device_master
# MAGIC WHERE updated_at > (    SELECT COALESCE(MAX(updated_at), '1900-01-01') 
# MAGIC     FROM telecom_federated_wd36_fc.telecom_devices.device_master);

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from telecom_bronze.bronze_device_master2

# COMMAND ----------

# MAGIC %md
# MAGIC ###Silver Layer Load
# MAGIC STEP 7: CREATE SILVER TABLE WITH CDF ENABLED
# MAGIC
# MAGIC CDF allows you to track and read incremental changes (inserts, updates, deletes) made to a Delta table — instead of reading the entire table every time.

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from table_changes('telecom_silver.device_master_silver1', 0)

# COMMAND ----------

# MAGIC %sql
# MAGIC     
# MAGIC CREATE TABLE IF NOT EXISTS telecom_silver.silver_device_master2 (
# MAGIC   device_id INT, device_type STRING, brand STRING, model STRING, os STRING, 
# MAGIC   owner_customer_id INT, status STRING, updated_at TIMESTAMP
# MAGIC ) TBLPROPERTIES (delta.enableChangeDataFeed = true);
# MAGIC
# MAGIC -- Step 1: Upsert (Insert + Update) from Bronze
# MAGIC MERGE INTO telecom_silver.silver_device_master2 AS target
# MAGIC USING (
# MAGIC   SELECT * FROM (
# MAGIC     -- Deduplicate Bronze: If a device came in 5 times today, only grab the latest one
# MAGIC     SELECT *, ROW_NUMBER() OVER (PARTITION BY device_id ORDER BY updated_at DESC) as rank
# MAGIC     FROM telecom_bronze.bronze_device_master2
# MAGIC   ) WHERE rank = 1
# MAGIC ) AS source
# MAGIC ON target.device_id = source.device_id
# MAGIC WHEN MATCHED AND target.updated_at != source.updated_at THEN 
# MAGIC   UPDATE SET *
# MAGIC WHEN NOT MATCHED THEN 
# MAGIC   INSERT *;
# MAGIC
# MAGIC -- Step 2: Delete records no longer present in the live MySQL source
# MAGIC DELETE FROM telecom_silver.silver_device_master2
# MAGIC WHERE device_id NOT IN (
# MAGIC   SELECT device_id FROM telecom_federated_wd36_fc.telecom_devices.device_master
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from table_changes('telecom_silver.silver_device_master2', 0)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Gold Layer Load
# MAGIC **STEP 8: CREATE GOLD TABLE WITH SCD TYPE 1 & TYPE 2**
# MAGIC
# MAGIC The Gold layer represents the final, business-ready state of your data, typically organized into dimensional models (facts and dimensions). To keep this layer updated efficiently, we utilize Delta Lake's Change Data Feed (CDF) from the Silver layer. 
# MAGIC
# MAGIC CDF allows you to track and read incremental row-level changes (`insert`, `update_preimage`, `update_postimage`, `delete`) made to a Silver Delta table. Instead of scanning and recalculating the entire dataset every time a pipeline runs, you only process the exact changes, dramatically reducing compute costs and processing time for Slowly Changing Dimensions (SCD).

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from telecom_gold.device_master_scd1

# COMMAND ----------

# MAGIC %sql
# MAGIC     
# MAGIC CREATE TABLE IF NOT EXISTS telecom_gold.device_master_scd1 (
# MAGIC   device_id INT, device_type STRING, brand STRING, model STRING, os STRING, owner_customer_id INT, status STRING, updated_at TIMESTAMP, ingestion_time TIMESTAMP
# MAGIC );
# MAGIC
# MAGIC MERGE INTO telecom_gold.device_master_scd1 AS target
# MAGIC USING (
# MAGIC   SELECT * FROM (
# MAGIC     SELECT *, ROW_NUMBER() OVER (PARTITION BY device_id ORDER BY _commit_version DESC, _change_type DESC) as rank
# MAGIC     FROM table_changes('telecom_silver.silver_device_master', 0)
# MAGIC   ) WHERE rank = 1
# MAGIC ) AS source
# MAGIC ON target.device_id = source.device_id
# MAGIC WHEN MATCHED AND source._change_type = 'delete' THEN 
# MAGIC   DELETE
# MAGIC WHEN MATCHED AND source._change_type IN ('insert', 'update_postimage') THEN 
# MAGIC   UPDATE SET 
# MAGIC     target.device_type = source.device_type,
# MAGIC     target.brand = source.brand,
# MAGIC     target.model = source.model,
# MAGIC     target.os = source.os,
# MAGIC     target.owner_customer_id = source.owner_customer_id,
# MAGIC     target.status = source.status,
# MAGIC     target.updated_at = source.updated_at,
# MAGIC     target.ingestion_time = current_timestamp()
# MAGIC WHEN NOT MATCHED AND source._change_type IN ('insert', 'update_postimage') THEN 
# MAGIC   INSERT (device_id, device_type, brand, model, os, owner_customer_id, status, updated_at, ingestion_time)
# MAGIC   VALUES (source.device_id, source.device_type, source.brand, source.model, source.os, source.owner_customer_id, source.status, source.updated_at, current_timestamp());

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from telecom_gold.device_master_scd1

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from telecom_gold.device_master_scd2

# COMMAND ----------

# MAGIC %sql
# MAGIC     
# MAGIC CREATE TABLE IF NOT EXISTS telecom_gold.device_master_scd2 (
# MAGIC   device_id INT, device_type STRING, brand STRING, model STRING, os STRING, owner_customer_id INT, status STRING,
# MAGIC   is_current BOOLEAN, start_date TIMESTAMP, end_date TIMESTAMP
# MAGIC );
# MAGIC
# MAGIC WITH silver_changes AS (
# MAGIC   SELECT * FROM (
# MAGIC     SELECT *, ROW_NUMBER() OVER (PARTITION BY device_id ORDER BY _commit_version DESC, _change_type DESC) as rank
# MAGIC     FROM table_changes('telecom_silver.silver_device_master', 0)
# MAGIC     WHERE _change_type IN ('insert', 'update_postimage', 'delete')
# MAGIC   ) WHERE rank = 1
# MAGIC ),
# MAGIC scd2_merge_data AS (
# MAGIC   SELECT device_id as merge_key, * FROM silver_changes
# MAGIC   UNION ALL
# MAGIC   SELECT NULL as merge_key, * FROM silver_changes WHERE _change_type = 'update_postimage'
# MAGIC )
# MAGIC
# MAGIC MERGE INTO telecom_gold.device_master_scd2 AS target
# MAGIC USING scd2_merge_data AS source
# MAGIC ON target.device_id = source.merge_key
# MAGIC
# MAGIC -- Close out old records
# MAGIC WHEN MATCHED AND target.is_current = true AND source._change_type IN ('update_postimage', 'delete') THEN
# MAGIC   UPDATE SET target.is_current = false, target.end_date = source.updated_at
# MAGIC
# MAGIC -- Insert new records
# MAGIC WHEN NOT MATCHED AND source._change_type IN ('insert', 'update_postimage') THEN
# MAGIC   INSERT (device_id, device_type, brand, model, os, owner_customer_id, status, is_current, start_date, end_date)
# MAGIC   VALUES (source.device_id, source.device_type, source.brand, source.model, source.os, source.owner_customer_id, source.status, true, source.updated_at, '9999-12-31T23:59:59.000Z');

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from telecom_gold.device_master_scd2

