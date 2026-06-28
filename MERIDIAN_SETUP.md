Meridian (Local Prototype)

This file explains how to set up the local-model prototype for `Meridian`, the product-guide chatbot.

Install (recommended in the project's virtualenv):

```powershell
pip install transformers torch
# Optionally install a CPU-only wheel for torch if needed (see https://pytorch.org)
```

Run backend (make sure uvicorn is running on port 8000):

```powershell
uvicorn aval_backend:app --reload --host 0.0.0.0 --port 8000
```

Run Streamlit frontend from project root:

```powershell
streamlit run app.py
```

Usage:
- Open the Streamlit app and go to the "Meridian — Product Guide" page.
- Ask about project features, navigation, or how to run simulations.

Notes:
- The prototype uses `distilgpt2` via `transformers` for short replies; it's intended as a lightweight demo and may produce generic text. Meridian's recommended mode is the canned, feature-focused replies provided when you ask about "features" or "capabilities".
- If you prefer not to install `torch`, Meridian will still answer feature-related questions from the canned list.
