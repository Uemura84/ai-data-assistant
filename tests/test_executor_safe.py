# tests/test_executor_safe.py
import pandas as pd
from core.executor import run_plan

def test_filter_basic():
    df = pd.DataFrame({"sales":[10,200,50], "region":["A","B","A"]})
    payload, kind, code = run_plan(df, {"action":"filter","predicates":"sales > 100 and region == 'B'"})
    assert kind == "table"
    assert len(payload) == 1
    assert payload.iloc[0]["sales"] == 200

def test_filter_block_atsign():
    df = pd.DataFrame({"x":[1,2,3]})
    try:
        run_plan(df, {"action":"filter","predicates":"x > @y"})
        assert False, "Should have rejected @ references"
    except Exception as e:
        assert "Unsupported expression" in str(e)

def test_unknown_column():
    df = pd.DataFrame({"a":[1,2]})
    try:
        run_plan(df, {"action":"aggregate","agg":"mean","column":"b"})
        assert False, "Should fail"
    except Exception as e:
        assert "not found" in str(e)
