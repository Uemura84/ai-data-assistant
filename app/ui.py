
import streamlit as st
import pandas as pd
from core.df_io import load_csv, infer_schema
from app.controller import handle_question

def render_ui():
    st.title("AI Data Assistant — Week 1 MVP")
    st.caption("Upload a CSV → ask a question → see generated code and results")

    with st.sidebar:
        st.subheader("Sample questions")
        st.write("- average `<numeric_col>`")
        st.write("- sum of `<numeric_col>` by `<category_col>`")
        st.write("- rows where `<numeric_col>` > 100 and `<category_col>` == 'A'")
        st.write("- how many unique `<category_col>`?")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded is None:
        st.info("Upload a CSV to get started.", icon="ℹ️")
        return

    df = load_csv(uploaded)
    if df is None or df.empty:
        st.error("Could not read CSV or it's empty.")
        return

    st.subheader("Preview")
    st.dataframe(df.head(50), use_container_width=True)
    schema = infer_schema(df)
    with st.expander("Detected schema"):
        st.json(schema)

    question = st.text_input("Ask a question about your data")
    if st.button("Run", type="primary") and question.strip():
        with st.spinner("Thinking..."):
            result = handle_question(question, df, schema)

        # app/ui.py (after result)
        st.subheader("Generated Code")
        st.code(result.get("code", ""), language="python")

        kind = result.get("kind")
        payload = result.get("payload")

        if kind == "table" and getattr(payload, "shape", (0,0))[0] >= 50:
            st.caption("Showing first 50 rows. Refine your query for more focused results.")

        if kind == "message":
            st.info("Tip: Try queries like “average <num_col> by <cat_col>”, "
                    "“rows where <num_col> > 100 and <cat_col> == 'A'”, "
                    "“top 5 <group_col> by <num_col>”.")

        if kind == "scalar":
            st.metric(label="Answer", value=str(payload))
        elif kind == "table":
            st.dataframe(payload, use_container_width=True)
        elif kind == "message":
            st.warning(payload)
        else:
            st.info("No result to display.")
