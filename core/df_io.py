from io import StringIO
import pandas as pd

def load_csv(uploaded_file) -> pd.DataFrame | None:
    try:
        data = uploaded_file.read()
        try:
            s = data.decode('utf-8')
        except UnicodeDecodeError:
            s = data.decode('latin-1')
        return pd.read_csv(StringIO(s))
    except Exception:
        return None

def infer_schema(df: pd.DataFrame) -> dict:
    cols = {col: str(dtype) for col, dtype in df.dtypes.items()}
    use_llm = False
    try:
        import streamlit as st
        use_llm = bool(st.session_state.get("use_llm", False))
    except Exception:
        pass
    return {"columns": cols, "row_count": int(len(df)), "_use_llm": use_llm}
