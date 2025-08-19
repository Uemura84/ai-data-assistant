
from typing import Dict, Any
import pandas as pd
from core.codegen import question_to_plan
from core.executor import run_plan

def handle_question(question: str, df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
    # Step 1: Build a plan (rule-based for now; LLM later)
    plan = question_to_plan(question, schema)

    # Step 2: Execute safely
    try:
        payload, kind, code = run_plan(df, plan)
        return {"payload": payload, "kind": kind, "code": code}
    except Exception as e:
        return {"payload": f"Error: {str(e)}", "kind": "message", "code": ""}
