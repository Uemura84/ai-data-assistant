import re
from typing import Dict, Any

def question_to_plan(question: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    q = question.lower().strip()

    # 1) Count distinct
    m = re.search(r"(unique|distinct)\s+(\w+)", q)
    if m:
        col = _normalize_col(m.group(2), schema)
        if col:
            return {"action":"count_distinct","column": col}

    # 2) Average/mean
    m = re.search(r"(average|mean)\s+of\s+(\w+)", q) or re.search(r"(average|mean)\s+(\w+)", q)
    if m:
        col = _normalize_col(m.group(2), schema)
        if col:
            g = re.search(r"by\s+(\w+)", q)
            group_by = []
            if g:
                group = _normalize_col(g.group(1), schema)
                if group:
                    group_by = [group]
            return {"action":"aggregate","agg":"mean","column": col, "group_by": group_by}

    # 3) Sum by group
    m = re.search(r"sum\s+of\s+(\w+)\s+by\s+(\w+)", q)
    if m:
        col = _normalize_col(m.group(1), schema)
        group = _normalize_col(m.group(2), schema)
        if col and group:
            return {"action":"aggregate","agg":"sum","column": col, "group_by":[group]}

    # 4) Filter rows with simple predicates
    if q.startswith("rows where"):
        preds = q.replace("rows where", "", 1).strip()
        return {"action":"filter","predicates": preds}

    # 5) Top-N
    m = re.search(r"top\s*(\d+)?\s*(\w+)\s+by\s+(\w+)", q)
    if m:
        n = int(m.group(1)) if m.group(1) else 5
        by = _normalize_col(m.group(3), schema)
        if by:
            return {"action":"top_n","by": by, "n": n, "ascending": False}

    return {"action":"message","text":"I couldn't parse that. Try: 'average sales by region' or 'rows where amount > 100'."}

def _normalize_col(name: str, schema: Dict[str, Any]) -> str | None:
    cols = list((schema or {}).get("columns", {}).keys())
    if name in cols:
        return name
    if name.endswith('s') and name[:-1] in cols:  # naive plural→singular
        return name[:-1]
    return name if name in cols else None
