# Fabric notebook source

# CELL ********************

# Build the customer dimension from bronze.
customers = spark.table("bronze.customers")
dim = customers.dropDuplicates(["customer_id"])
dim.write.mode("overwrite").saveAsTable("silver.dim_customers")

# METADATA ********************

# META {
# META   "language": "python"
# META }
