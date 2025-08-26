import re

_ALLOWED_OPS = {"==","!=",">=", "<=","<",">", "+","-","*","/","%","and","or","not","in"}
_NUM_RE = re.compile(r"(?:\d+\.\d*|\d*\.\d+|\d+)")

def sanitize_predicates(pred: str, columns: list[str]) -> str:
    s = pred.strip()
    if "@" in s or "__" in s:
        raise ValueError("Unsupported expression in filter.")
    tokens = _tokenize(s)
    for t in tokens:
        low = t.lower()
        if t in _ALLOWED_OPS or low in _ALLOWED_OPS:
            continue
        if t in columns:
            continue
        if _is_literal(t):
            continue
        if t in {"(",")",",","[","]","."}:
            continue
        if t in {"True","False","None"}:
            continue
        raise ValueError(f"Unsupported token in filter: {t}")
    return s

def _tokenize(s: str) -> list[str]:
    # words, numbers, comparison ops, parentheses/brackets/commas, single symbols
    parts = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+\.\d*|\d*\.\d+|\d+|==|!=|>=|<=|[()\[\],]|[^\sA-Za-z0-9_]", s)
    return [p for p in parts if p.strip()]

def _is_literal(tok: str) -> bool:
    if _NUM_RE.fullmatch(tok):
        return True
    if (tok.startswith("'") and tok.endswith("'")) or (tok.startswith('"') and tok.endswith('"')):
        return True
    return False
