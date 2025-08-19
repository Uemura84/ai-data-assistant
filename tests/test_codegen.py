
from core.codegen import question_to_plan

def test_mean():
    schema = {"columns": {"sales":"int64"}, "row_count": 10}
    p = question_to_plan("average sales by region", schema)
    assert p["action"] == "aggregate"
    assert p["agg"] == "mean"
