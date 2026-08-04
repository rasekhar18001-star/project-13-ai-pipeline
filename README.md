# Project 13: A Pipeline for an AI Application

This repository implements a production-minded RAG help desk for a fictional 2026 Christian school. It combines a fixed policy corpus, deterministic lexical retrieval, an OpenAI-compatible Ollama Cloud call, strict groundedness evaluation, drift monitoring, an error budget, and replay-based safe rollout controls. No policy is real operational guidance.

## Architecture and layout

`app/` contains retrieval, grounded generation, privacy-minimal telemetry, CLI, and FastAPI. `data/policies/` is the fixed corpus. `evals/` holds nine adversarial cases, the judge gate, and unfilled human-label template. `sre/` and `monitoring/` implement error budgets and PSI. `rollout/` and `deploy/` implement shadow comparison, metric-gated promotion, and rollback. `.github/workflows/ci.yml` runs install, lint, unit tests, secret scan, then the PR-only cloud evaluation.

## Install and local Ollama setup

Install Python 3.12 and Ollama, sign in with `ollama signin`, and ensure the local proxy is running. The local profile uses `http://localhost:11434/v1`, API key `ollama`, and pinned `gpt-oss:120b-cloud`. The model call is made through the official OpenAI Python SDK using Ollama's compatible API.

PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:OPENAI_BASE_URL='http://localhost:11434/v1'
$env:OPENAI_API_KEY='ollama'
$env:RAG_MODEL_ID='gpt-oss:120b-cloud'
$env:JUDGE_MODEL_ID='gpt-oss:120b-cloud'
```

Bash:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export RAG_MODEL_ID=gpt-oss:120b-cloud
export JUDGE_MODEL_ID=gpt-oss:120b-cloud
```

## Run the service and checks

```text
python -m uvicorn app.api:app --reload
python -m app.cli "How do I reset a staff password?"
python -m ruff check .
python -m pytest tests/unit -q
python -m evals.judge evals/cases.jsonl --min-groundedness 0.90
python scripts/run_error_budget_demo.py
python scripts/run_drift_demo.py
python -m rollout.shadow
python -m rollout.promote
python -m rollout.rollback
```

The challenger only receives replayed traffic and is never served. Promotion requires complete results, groundedness at least `0.90`, and performance no worse than champion. Rollback restores the recorded previous champion in one command.

## Human judge validation

The student must personally copy and complete `evals/human_labels.template.jsonl`; all `human_grounded` fields intentionally remain `null`. Then run `python -m evals.validate_judge your-completed-labels.jsonl --min-agreement 0.80`.

## GitHub Actions configuration

Open **Repository Settings → Secrets and variables → Actions** and create:

- Secret: `OPENAI_API_KEY` = the user's Ollama API key
- Variable: `OPENAI_BASE_URL` = `https://ollama.com/v1`
- Variable: `RAG_MODEL_ID` = `gpt-oss:120b`
- Variable: `JUDGE_MODEL_ID` = `gpt-oss:120b`

Local Ollama routes `gpt-oss:120b-cloud` through localhost; a hosted GitHub runner instead uses Ollama's direct cloud endpoint and `gpt-oss:120b`. CI has read-only contents permission and runs the paid eval only for pull requests after all deterministic gates pass.

## Regression demonstration

After initializing Git, committing a clean `main`, and configuring Git identity, run `python scripts/create_regression_branch.py`. It creates and optionally commits `regression-demo` but never pushes. Push it manually with `git push -u origin regression-demo`, open a PR, and retain the real failed CI link or screenshot. Return with `git switch main`.
