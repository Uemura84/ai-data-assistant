
# Safe execution for a restricted set of actions.
# Returns: (payload, kind, code)

from typing import Dict, Any, Tuple
import pandas as pd

def run_plan(df: pd.DataFrame, plan: Dict[str, Any]) -> Tuple[Any, str, str]:
    action = plan.get("action")

    if action == "count_distinct":
        col = plan.get("column")
        code = f"df['{col}'].nunique()"
        _check_col(df, col)
        value = df[col].nunique()
        return value, "scalar", code

    if action == "aggregate":
        col = plan.get("column")
        agg = plan.get("agg", "sum")
        group_by = plan.get("group_by", [])
        _check_col(df, col)
        for g in group_by:
            _check_col(df, g)
        if group_by:
            code = f"df.groupby({group_by})['{col}'].{agg}().reset_index()"
            out = df.groupby(group_by)[col].agg(agg).reset_index()
        else:
            code = f"df['{col}'].{agg}()"
            out = pd.DataFrame({col:[getattr(df[col], agg)()]})
        return out.head(50), "table", code

    if action == "filter":
        predicates = plan.get("predicates", "")
        # Note: df.query is still a string; user-supplied; warn and limit surface
        # Minimal sanitation (best effort). In production, build a proper parser.
        code = f"df.query({predicates!r})"
        try:
            out = df.query(predicates)
        except Exception as e:
            raise ValueError(f"Invalid filter: {e}")
        return out.head(50), "table", code

    if action == "top_n":
        by = plan.get("by")
        n = int(plan.get("n", 5))
        ascending = bool(plan.get("ascending", False))
        _check_col(df, by)
        code = f"df.sort_values(by='{by}', ascending={ascending}).head({n})"
        out = df.sort_values(by=by, ascending=ascending).head(n)
        return out, "table", code

    if action == "message":
        return plan.get("text", "No message"), "message", ""

    return "Unsupported action.", "message", ""

def _check_col(df: pd.DataFrame, col: str):
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found. Available: {list(df.columns)}")
