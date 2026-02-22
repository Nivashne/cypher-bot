# SREC Cypher Bot

A cybersecurity-aware RAG chatbot for college information with policy and confidentiality controls.

## Project Structure

```
SREC_Cypher_Bot/
│
├── assets/
│   ├── logo.png                # optional default logo
│   ├── logo.jpg                # optional default logo
│   └── logo.jpeg               # optional default logo
├── data/
│   ├── admissions.txt
│   ├── campus_rules.txt
│   ├── placements.txt
│   └── confidential_budget.txt
│
├── embeddings/
├── db/
│   └── logs.db
│
├── policy_guard.py
├── validator.py
├── retriever.py
├── engine.py
├── ingest.py
├── ui.py
└── requirements.txt
```

## Run

```bash
pip install -r requirements.txt
python ingest.py
python -m streamlit run ui.py
```

## Logo Setup

- Place your logo image at one of:
  - `SREC_Cypher_Bot/assets/logo.png`
  - `SREC_Cypher_Bot/assets/logo.jpg`
  - `SREC_Cypher_Bot/assets/logo.jpeg`
- The UI will automatically load the first available one.
- You can still override it at runtime using the **Upload Logo (optional)** control.

## Security Workflow

1. `policy_guard.py` blocks sensitive prompts.
2. `retriever.py` retrieves relevant docs from Chroma.
3. `validator.py` removes confidential docs.
4. `engine.py` returns refusal if unsafe/no safe context, else generates a contextual answer.
5. Every query is logged in `db/logs.db` with status:
   - `ALLOWED`
   - `BLOCKED_POLICY`
   - `BLOCKED_CONFIDENTIAL`

## Fixing "streamlit not installed" / ERR_EMPTY_RESPONSE

If you see:
- `No module named streamlit`
- Playwright `ERR_EMPTY_RESPONSE` on `http://127.0.0.1:8501`

follow this exact flow:

```bash
cd /workspace/cypher-bot/SREC_Cypher_Bot
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python ingest.py
python -m streamlit run ui.py --server.headless true --server.port 8501
```

Then open in browser:
- `http://127.0.0.1:8501`

### Notes
- `sqlite3` is part of Python standard library, so it should **not** be installed with pip.
- If your environment is behind a proxy/firewall, configure pip before install:

```bash
pip config set global.proxy http://<user>:<pass>@<host>:<port>
```

- If install still fails, test with:

```bash
python -m pip index versions streamlit
python -c "import streamlit; print(streamlit.__version__)"
```
