# Fabric notebook source

# CELL ********************

# Ingest raw customers into the bronze layer.
df = spark.read.option("header", True).csv("Files/landing/customers.csv")
df.write.mode("overwrite").saveAsTable("bronze.customers")

# METADATA ********************

# META {
# META   "language": "python"
# META }
