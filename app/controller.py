from typing import Dict, Any
import os
import pandas as pd
from core.codegen import question_to_plan
from core.executor import run_plan
from core.plan import Plan
from pydantic import ValidationError
from app.llm import llm_question_to_plan

def handle_question(question: str, df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
    # Step 1: Rule-based plan
    raw_plan = question_to_plan(question, schema)
    source = "rules"

    # If rules returned a generic "message", try LLM if enabled via UI
    use_llm = bool(schema.get("_use_llm", False)) or os.environ.get("USE_LLM") == "1"
    if raw_plan.get("action") == "message" and use_llm:
        llm_plan = llm_question_to_plan(question, schema)
        if llm_plan:
            raw_plan = llm_plan
            source = "llm"

    # Step 2: Validate (strict)
    try:
        plan = Plan.model_validate(raw_plan)
    except ValidationError as e:
        return {"payload": f"Invalid request: {e.errors()}", "kind": "message", "code": "", "source": source}

    # Step 3: Execute safely
    try:
        payload, kind, code = run_plan(df, plan.model_dump())
        return {"payload": payload, "kind": kind, "code": code, "source": source}
    except Exception as e:
        return {"payload": f"Error: {str(e)}", "kind": "message", "code": "", "source": source}
