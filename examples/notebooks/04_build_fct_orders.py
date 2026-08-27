# Fabric notebook source

# CELL ********************

# Join orders with the customer dimension into a fact table.
orders = spark.table("bronze.orders")
dim = spark.table("silver.dim_customers")
fct = orders.join(dim, "customer_id")
fct.write.mode("overwrite").saveAsTable("silver.fct_orders")

# METADATA ********************

# META {
# META   "language": "python"
# META }
