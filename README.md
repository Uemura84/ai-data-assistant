
# AI Data Assistant — Week 1 MVP (CSV Q&A with LLM)

A minimal Streamlit app that lets you upload a CSV and ask questions.
Week 1 focuses on: CSV load/preview, rule-based plan generator (stub), safe execution (stub), and LLM-ready structure.

## Quickstart

```bash
# 1) Create & activate a virtualenv (macOS/Linux)
python -m venv .venv && source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run the app
streamlit run streamlit_app.py
```

> Configure API keys later (Week 1, Thu) by copying `.env.example` to `.env`.

## Project Layout
```
ai-data-assistant/
├─ app/
│  ├─ __init__.py
│  ├─ ui.py
│  ├─ controller.py
│  └─ llm.py
├─ core/
│  ├─ df_io.py
│  ├─ codegen.py
│  └─ executor.py
├─ tests/
│  ├─ test_codegen.py
│  └─ test_executor.py
├─ data/                  # sample CSVs (place yours here)
├─ .env.example
├─ requirements.txt
├─ README.md
└─ streamlit_app.py
```

## Milestones (Week 1)
- [x] Repo scaffold
- [ ] Rule-based NL → plan
- [ ] Safe executor
- [ ] LLM plan (fallback to rule-based)
- [ ] README updates + short demo

## Notes
- Keep *only* allowlisted pandas ops in execution.
- Never expose stack traces in the UI.
