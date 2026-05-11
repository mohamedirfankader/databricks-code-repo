from pyspark import pipelines as dp

dp.create_streaming_table(
    name="telecom_gold.device_master_gold_scd1_6",
    comment="No Historical tracking of device master data changes (SCD Type 1)."
)

dp.apply_changes(
    target="telecom_gold.device_master_gold_scd1_6",
    source="telecom_silver.device_master_silver_6", 
    keys=["device_id"],                               
    sequence_by="updated_at", 
    apply_as_deletes="status = 'Inactive'",
    stored_as_scd_type=1)