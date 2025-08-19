
# Rule-based NL → plan (Week 1, Tue). Very small set of intents.
# The plan is a JSON-like dict that the executor understands.
# Example:
#  {"action":"aggregate","agg":"mean","column":"sales","group_by":["region"]}

import re
from typing import Dict, Any

def question_to_plan(question: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    q = question.lower().strip()

    # 1) Count distinct
    m = re.search(r"(unique|distinct)\s+(\w+)", q)
    if m:
        col = m.group(2)
        return {"action":"count_distinct","column": col}

    # 2) Average/mean
    m = re.search(r"(average|mean)\s+of\s+(\w+)", q)
    if not m:
        m = re.search(r"(average|mean)\s+(\w+)", q)
    if m:
        col = m.group(2)
        # optional: group by
        g = re.search(r"by\s+(\w+)", q)
        group_by = [g.group(1)] if g else []
        return {"action":"aggregate","agg":"mean","column": col, "group_by": group_by}

    # 3) Sum by group
    m = re.search(r"sum\s+of\s+(\w+)\s+by\s+(\w+)", q)
    if m:
        col = m.group(1)
        group = m.group(2)
        return {"action":"aggregate","agg":"sum","column": col, "group_by":[group]}

    # 4) Filter rows with simple predicates (>, <, ==, >=, <=)
    # example: rows where sales > 100 and region == 'A'
    if q.startswith("rows where"):
        preds = q.replace("rows where", "").strip()
        return {"action":"filter","predicates": preds}

    # 5) Top-N by numeric column (default n=5)
    m = re.search(r"top\s*(\d+)?\s*(\w+)\s+by\s+(\w+)", q)
    if m:
        n = int(m.group(1)) if m.group(1) else 5
        by = m.group(3)
        return {"action":"top_n","by": by, "n": n, "ascending": False}

    # Fallback: show columns available
    return {"action":"message","text":"I couldn't parse that. Try: 'average sales by region' or 'rows where amount > 100'."}
