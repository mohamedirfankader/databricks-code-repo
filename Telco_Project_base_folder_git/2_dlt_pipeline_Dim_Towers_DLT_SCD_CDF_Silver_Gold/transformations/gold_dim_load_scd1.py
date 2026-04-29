import dlt

# ====================================================================
# 2. GOLD LAYER: SCD TYPE 1 (CDF Enabled + Hard Deletes)
# ====================================================================

# 1. Initialize the target streaming table in the Gold schema
dlt.create_streaming_table(
    name="telecom_gold.dim_towers1_gold_scd1",
    comment="Current status of network towers. No historical tracking (SCD Type 1). CDF Enabled.",
    table_properties={"delta.enableChangeDataFeed": "true"} 
)

# 2. Apply the CDC changes from the Silver table
dlt.apply_changes(
    target="telecom_gold.dim_towers1_gold_scd1",
    source="telecom_silver.dim_towers1_silver", # Reading from cleaned Silver table
    keys=["tower_id"],                        # The primary key for the tower dimension
    sequence_by="updated_at",                 # Ensures the latest update wins if data arrives out of order
    apply_as_deletes="network_type = 'DECOM'", # Applying hard deletes if the source system marks a tower for decommissioning
    stored_as_scd_type=1 )