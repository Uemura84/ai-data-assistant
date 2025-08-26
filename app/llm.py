from typing import Dict, Any
import os, json
from pydantic import BaseModel
from dotenv import load_dotenv

# OpenAI SDK (1.x)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

load_dotenv()

class LLMPlan(BaseModel):
    action: str
    column: str | None = None
    agg: str | None = None
    group_by: list[str] | None = None
    predicates: str | None = None
    by: str | None = None
    n: int | None = 5
    ascending: bool | None = False
    text: str | None = None

SYSTEM_PROMPT = """You translate questions about a given CSV schema into a JSON plan.
Only use columns from the provided schema. Prefer simple ops: filters, aggregations,
groupby, counts, top-N, distinct. Return ONLY a JSON object, no code, no explanations.
"""

def llm_question_to_plan(question: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("MODEL", "gpt-4o-mini")
    if not api_key or OpenAI is None:
        return {}

    client = OpenAI(api_key=api_key)

    schema_cols = list((schema or {}).get("columns", {}).keys())
    schema_json = {"columns": schema_cols}

    messages = [
        {"role":"system", "content": SYSTEM_PROMPT + f"\nSchema: {json.dumps(schema_json)}"},
        {"role":"user", "content": question}
    ]

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type":"json_object"},
            temperature=0.0,
        )
        content = resp.choices[0].message.content
        data = json.loads(content)
        plan = LLMPlan(**data).model_dump()
        return plan
    except Exception:
        # Fail safe: keep rules-only behavior
        return {}
