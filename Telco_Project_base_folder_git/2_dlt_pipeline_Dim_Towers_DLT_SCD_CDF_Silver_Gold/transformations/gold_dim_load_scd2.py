import dlt

# ====================================================================
# 3. GOLD LAYER: SCD TYPE 2 (Historical Tracking + Soft Deletes)
# ====================================================================
dlt.create_streaming_table(
    name="telecom_gold.dim_towers1_gold_scd2",
    comment="Historical tracking of tower data changes (SCD Type 2). Maintains full version history."
)

dlt.apply_changes(
    target="telecom_gold.dim_towers1_gold_scd2",
    source="telecom_silver.dim_towers1_silver", # Cleaned Silver data source 
    keys=["tower_id"],                        # Primary key
    sequence_by="updated_at",                 # Ensures the latest row wins if data arrives out of order
    
    # Decommissioned towers will be marked as soft deleted (updated_at) in the SCD history 
    apply_as_deletes="network_type = 'DECOM'", 
    stored_as_scd_type=2,    
    # Specify columns that trigger a new historical row when they change 
    track_history_column_list=[
        "tower_name", 
        "city", 
        "state", 
        "region", 
        "network_type" ] )