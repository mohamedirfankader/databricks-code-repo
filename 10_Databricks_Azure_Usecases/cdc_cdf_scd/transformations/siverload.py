import dlt as dp
#DP offers us - We don't need to say how to do it, we have to say what to do it in declarative pipeline.
@dp.table(
    name="telecom_silver.device_master_silver_6",
    comment="Staged silver data. CDF is enabled here that maintains some interal flag such as _change_type (insert/update_preimage/update_postimage/delete) to help downstream gold processing efficiently by avoiding full table scan",
    table_properties={"delta.enableChangeDataFeed": "true"} )
def load_data_silver_imp_dp():
    return spark.readStream.table("telecom_bronze.bronze_device_master_6")
    #readStream will only collect newly inserted data - (inserted data in DB got inserted into bronze)/appended (updated/deleted data in DB got inserted into bronze) data from the source, by internally maintaining some checkpoint/watermarking