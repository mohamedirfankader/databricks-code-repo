from pyspark import pipelines as dp

dp.create_streaming_table(
    name="telecom_gold.device_master_gold_scd2_6",
    comment="Historical tracking of device master data changes (SCD Type 2)."
)

dp.apply_changes(
    target="telecom_gold.device_master_gold_scd2_6",
    source="telecom_silver.device_master_silver_6", 
    keys=["device_id"],
    sequence_by="updated_at", 
    apply_as_deletes="status = 'Inactive'",
    stored_as_scd_type=2,
    track_history_column_list=[
        "device_type", 
        "brand", 
        "model", 
        "os", 
        "owner_customer_id"    ]
)