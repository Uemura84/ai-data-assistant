# core/sanitize.py
import re

_ALLOWED_OPS = {"==","!=",">=", "<=","<",">", "+","-","*","/","%","and","or","not","in"}
_ID_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_NUM_RE = re.compile(r"""(?x)
    (?:\d+\.\d*|\d*\.\d+|\d+)   # 12, 12., .12, 12.34
""")

def sanitize_predicates(pred: str, columns: list[str]) -> str:
    s = pred.strip()

    # 1) quick bans
    if "@" in s or "__" in s:
        raise ValueError("Unsupported expression in filter.")

    # 2) tokenize identifiers and validate they are either:
    #    - allowed operators/keywords
    #    - string/number literals
    #    - column names
    tokens = _tokenize(s)
    for t in tokens:
        low = t.lower()
        if t in _ALLOWED_OPS or low in _ALLOWED_OPS:
            continue
        if t in columns:
            continue
        if _is_literal(t):
            continue
        # Allow parentheses and commas
        if t in {"(",")",",","[","]"}:
            continue
        # Keywords True/False/None
        if t in {"True","False","None"}:
            continue
        # Otherwise reject
        raise ValueError(f"Unsupported token in filter: {t}")

    return s

def _tokenize(s: str) -> list[str]:
    # Split on whitespace and typical symbols, keep brackets/parens
    parts = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+\.\d*|\d*\.\d+|\d+|==|!=|>=|<=|[()\,\[\]]|[^\sA-Za-z0-9_]", s)
    # Merge standalone symbols like > or < with = handled above; remaining single char ops are fine
    return [p for p in parts if p.strip()]

def _is_literal(tok: str) -> bool:
    # number?
    if _NUM_RE.fullmatch(tok):
        return True
    # quoted string?
    if (tok.startswith("'") and tok.endswith("'")) or (tok.startswith('"') and tok.endswith('"')):
        return True
    return False
