# Databricks notebook source
# MAGIC %md
# MAGIC #Creating this child notebook for the demo of calling child notebook from the parent notebook

# COMMAND ----------

dbutils.widgets.text("table_name", "cities")
table_name = dbutils.widgets.get("table_name")
print(f"parameter passed is {table_name}")
spark.sql(f"select * from {table_name}").show(2)

# COMMAND ----------

dbutils.notebook.exit("success")
