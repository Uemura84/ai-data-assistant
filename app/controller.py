from core.codegen import question_to_plan
from core.executor import run_plan
from core.plan import Plan
from pydantic import ValidationError
#import pdb  # For debugging purposes

def handle_question(question, df, schema):
    #pdb.set_trace()
    raw_plan = question_to_plan(question, schema)
    try:
        plan = Plan.model_validate(raw_plan)  # raises on invalid
    except ValidationError as e:
        return {"payload": f"Invalid request: {e.errors()}", "kind":"message", "code": ""}

    try:
        payload, kind, code = run_plan(df, plan.model_dump())
        return {"payload": payload, "kind": kind, "code": code}
    except Exception as e:
        return {"payload": f"Error: {str(e)}", "kind": "message", "code": ""}
