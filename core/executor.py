# core/executor.py
from typing import Dict, Any, Tuple
import pandas as pd
from core.sanitize import sanitize_predicates

_ROW_CAP = 50
_ALLOWED_AGGS = {"mean","sum","min","max","median","count"}

def run_plan(df: pd.DataFrame, plan: Dict[str, Any]) -> Tuple[Any, str, str]:
    action = plan.get("action")
    cols = set(df.columns)

    if action == "count_distinct":
        col = _require_col(plan, "column", cols)
        code = f"df['{col}'].nunique()"
        value = df[col].nunique()
        return value, "scalar", code

    if action == "aggregate":
        col = _require_col(plan, "column", cols)
        
        # inside aggregate branch, before computing agg
        if df[col].dtype.kind not in "biufc":  # bool,int,unsigned,float,complex
            # attempt safe coercion
            coerced = pd.to_numeric(df[col], errors="coerce")
            if coerced.notna().sum() == 0:
                raise ValueError(f"Column '{col}' is not numeric and cannot be coerced.")
            df = df.copy()
            df[col] = coerced

        agg = plan.get("agg", "sum")
        if agg not in _ALLOWED_AGGS:
            raise ValueError(f"Aggregation '{agg}' is not allowed.")
        group_by = plan.get("group_by") or []
        for g in group_by:
            _ensure_col(g, cols)
        if group_by:
            code = f"df.groupby({group_by})['{col}'].{agg}().reset_index()"
            out = df.groupby(group_by)[col].agg(agg).reset_index()
        else:
            code = f"df['{col}'].{agg}()"
            out = pd.DataFrame({col:[getattr(df[col], agg)()]})
        return out.head(_ROW_CAP), "table", code

    if action == "filter":
        raw = plan.get("predicates", "")
        safe = sanitize_predicates(raw, list(cols))
        code = f"df.query({safe!r}, engine='python')"
        try:
            out = df.query(safe, engine="python")
        except Exception as e:
            raise ValueError(f"Invalid filter: {e}")
        return out.head(_ROW_CAP), "table", code

    if action == "top_n":
        by = _require_col(plan, "by", cols)
        n = int(plan.get("n", 5))
        ascending = bool(plan.get("ascending", False))
        code = f"df.sort_values(by='{by}', ascending={ascending}).head({n})"
        out = df.sort_values(by=by, ascending=ascending).head(n)
        return out, "table", code

    if action == "message":
        return plan.get("text", "No message"), "message", ""

    return "Unsupported action.", "message", ""

# --- helpers ---
def _require_col(plan: Dict[str, Any], key: str, cols: set) -> str:
    val = plan.get(key)
    if not isinstance(val, str):
        raise ValueError(f"Missing '{key}'.")
    _ensure_col(val, cols)
    return val

def _ensure_col(name: str, cols: set):
    if name not in cols:
        raise ValueError(f"Column '{name}' not found. Available: {sorted(cols)}")
