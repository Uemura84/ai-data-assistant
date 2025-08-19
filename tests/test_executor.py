
import pandas as pd
from core.executor import run_plan

def test_count_distinct():
    df = pd.DataFrame({"region": ["A","A","B","C"]})
    payload, kind, code = run_plan(df, {"action":"count_distinct","column":"region"})
    assert kind == "scalar"
    assert payload == 3
