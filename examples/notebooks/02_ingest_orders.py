# Fabric notebook source

# CELL ********************

# Ingest raw orders into the bronze layer.
df = spark.read.option("header", True).csv("Files/landing/orders.csv")
df.write.mode("overwrite").saveAsTable("bronze.orders")

# METADATA ********************

# META {
# META   "language": "python"
# META }
