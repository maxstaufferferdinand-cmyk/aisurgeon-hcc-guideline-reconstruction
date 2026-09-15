# AGENTS.md

Project-specific instructions for Codex work in this repository.

## Scope

This repository contains reproducibility code for the ESMO HCC 2012 to 2025
living-evidence guideline reconstruction pipeline. It must remain independent
from earlier disease-specific repositories and must not contain generated
scientific run data.

## Rules

- Do not commit or push unless the user explicitly asks.
- Do not change scientific logic, prompts, evidence rules, model names, search
  dates, or output schemas without explicit user approval.
- Do not print environment variables, API keys, tokens, credential values, or
  `.env` contents.
- Do not add PubMed XML, CSV/JSONL datasets, provider inputs or outputs, logs,
  PDFs, DOCX files, ZIP archives, or credentials to the repository.
- Keep dependency changes minimal and review `pyproject.toml` and `uv.lock`
  together.
- Smoke tests and repository-policy tests must not call PubMed, OpenAI, Gemini,
  or other external APIs.
