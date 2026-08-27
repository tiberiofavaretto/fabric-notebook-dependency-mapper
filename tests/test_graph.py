import pytest

from depmapper.config import Config
from depmapper.extract import TableRefs
from depmapper.graph import CycleError, DependencyGraph
from depmapper.cli import build_graph


def _graph_from(mapping):
    graph = DependencyGraph()
    for name, (reads, writes) in mapping.items():
        graph.add(name, TableRefs(reads=set(reads), writes=set(writes)))
    return graph


def test_dependencies_and_levels():
    graph = _graph_from(
        {
            "01_ingest_customers": ([], ["bronze.customers"]),
            "02_ingest_orders": ([], ["bronze.orders"]),
            "03_dim_customers": (["bronze.customers"], ["silver.dim_customers"]),
            "04_fct_orders": (["bronze.orders", "silver.dim_customers"], ["silver.fct_orders"]),
            "05_daily_sales": (["silver.fct_orders"], ["gold.daily_sales"]),
        }
    )
    deps = graph.dependencies()
    assert deps["03_dim_customers"] == {"01_ingest_customers"}
    assert deps["04_fct_orders"] == {"02_ingest_orders", "03_dim_customers"}
    assert deps["05_daily_sales"] == {"04_fct_orders"}

    levels = graph.topological_levels()
    assert levels[0] == ["01_ingest_customers", "02_ingest_orders"]
    assert levels[-1] == ["05_daily_sales"]


def test_cycle_is_detected():
    graph = _graph_from(
        {
            "a": (["silver.b"], ["silver.a"]),
            "b": (["silver.a"], ["silver.b"]),
        }
    )
    with pytest.raises(CycleError):
        graph.topological_levels()


def test_mermaid_contains_edges():
    graph = _graph_from(
        {
            "producer": ([], ["silver.t"]),
            "consumer": (["silver.t"], []),
        }
    )
    mermaid = graph.to_mermaid()
    assert "flowchart LR" in mermaid
    assert "producer[producer] --> consumer[consumer]" in mermaid


def test_build_graph_on_examples():
    graph = build_graph("examples/notebooks", Config())
    assert set(graph.notebooks) == {
        "01_ingest_customers",
        "02_ingest_orders",
        "03_build_dim_customers",
        "04_build_fct_orders",
        "05_daily_sales",
    }
    deps = graph.dependencies()
    assert deps["05_daily_sales"] == {"04_build_fct_orders"}
