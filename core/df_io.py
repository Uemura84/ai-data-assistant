
from io import BytesIO, StringIO
import pandas as pd

def load_csv(uploaded_file) -> pd.DataFrame | None:
    try:
        # Streamlit gives a file-like object; ensure UTF-8 by default
        data = uploaded_file.read()
        try:
            s = data.decode('utf-8')
        except UnicodeDecodeError:
            s = data.decode('latin-1')
        return pd.read_csv(StringIO(s))
    except Exception:
        return None

def infer_schema(df: pd.DataFrame) -> dict:
    schema = {}
    for col, dtype in df.dtypes.items():
        schema[col] = str(dtype)
    return {"columns": schema, "row_count": int(len(df))}
