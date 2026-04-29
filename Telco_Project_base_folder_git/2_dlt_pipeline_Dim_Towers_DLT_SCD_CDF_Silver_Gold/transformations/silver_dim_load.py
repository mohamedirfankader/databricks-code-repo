import dlt
from pyspark.sql.functions import col, upper, trim, when

# ====================================================================
# 1. SILVER LAYER: MATERIALIZED TABLE WITH TRANSFORMATIONS
# ====================================================================
@dlt.table(
    name="telecom_silver.dim_towers1_silver",
    comment="Cleaned and standardized tower silver data. Records without tower_id are dropped."
)
# Data Quality Expectation: Drop the row completely if tower_id is missing
@dlt.expect_or_drop("valid_tower_id", "tower_id IS NOT NULL")
def load_tower_silver():
    # Read the stream from the Bronze table created in the previous step, This automatically tracks changes using Spark Structured Streaming
    raw_stream = spark.readStream.table("telecom_bronze.bronze_dim_tower")
    
    # Apply Transformation Logics
    cleaned_stream = (
        raw_stream
        # 1. Standardize text: Uppercase the state and region for reporting consistency
        .withColumn("state", upper(trim(col("state"))))
        .withColumn("region", upper(trim(col("region"))))
        
        # 2. Clean up tower names and city: Remove trailing/leading spaces
        .withColumn("tower_name", trim(col("tower_name")))
        .withColumn("city", trim(col("city")))
        
        # 3. Standardize Network Type: Ensure '5g'/'4g' becomes '5G'/'4G'
        .withColumn("network_type", upper(trim(col("network_type"))))
    )
    
    return cleaned_stream