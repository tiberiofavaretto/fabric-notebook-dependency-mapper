from depmapper.config import DEFAULT_READ_SCHEMAS
from depmapper.extract import extract_refs


def test_saveastable_is_a_write():
    code = 'df.write.saveAsTable("bronze.customers")'
    refs = extract_refs(code, DEFAULT_READ_SCHEMAS)
    assert refs.writes == {"bronze.customers"}
    assert refs.reads == set()


def test_spark_table_is_a_read():
    code = 'customers = spark.table("bronze.customers")'
    refs = extract_refs(code, DEFAULT_READ_SCHEMAS)
    assert refs.reads == {"bronze.customers"}
    assert refs.writes == set()


def test_read_minus_self_write():
    code = """
    dim = spark.table("bronze.customers")
    dim.write.saveAsTable("silver.dim_customers")
    """
    refs = extract_refs(code, DEFAULT_READ_SCHEMAS)
    assert refs.reads == {"bronze.customers"}
    assert refs.writes == {"silver.dim_customers"}


def test_create_and_insert_and_backticks():
    code = """
    CREATE TABLE IF NOT EXISTS gold.report AS SELECT * FROM silver.fct_orders;
    INSERT INTO `gold`.`report` SELECT * FROM staging.extra;
    """
    refs = extract_refs(code, DEFAULT_READ_SCHEMAS)
    assert refs.writes == {"gold.report"}
    assert refs.reads == {"silver.fct_orders", "staging.extra"}


def test_comments_are_ignored():
    code = """
    -- FROM bronze.ignored_sql
    # spark.table("bronze.ignored_py")
    x = spark.table("bronze.kept")
    """
    refs = extract_refs(code, DEFAULT_READ_SCHEMAS)
    assert refs.reads == {"bronze.kept"}


def test_unknown_schema_is_ignored():
    code = 'df = spark.read.format("delta").load("/mnt/x")'
    refs = extract_refs(code, DEFAULT_READ_SCHEMAS)
    assert refs.reads == set()
    assert refs.writes == set()
