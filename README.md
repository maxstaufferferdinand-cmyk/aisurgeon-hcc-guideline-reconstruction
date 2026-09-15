# AISurgeon HCC Guideline Reconstruction

Research code for reproducing an autonomous living-evidence reconstruction of
the ESMO-ESDO HCC Clinical Practice Guideline 2012 using PubMed evidence
published from 2012-07-01 through 2025-02-28 inclusive.

This repository contains software only. It is for research and reproducibility
work. It is not a clinical guideline, not a clinical decision-support system,
and not a substitute for clinician judgment, society guidance, regulatory
review, or expert guideline-panel work.

Source guidelines, generated guideline documents, PubMed datasets, provider
payloads, and run outputs are not distributed in this repository.

## Research Purpose

The project tests whether a locked, auditable pipeline can reconstruct a
guideline update from a historical oncology guideline and a bounded evidence
window. The historical source is the ESMO-ESDO Clinical Practice Guideline for
hepatocellular carcinoma published in 2012. The pipeline extracts the historical
structure, builds source-derived evidence units, retrieves post-source PubMed
evidence, excludes guideline or consensus publications, maps and appraises the
remaining evidence, synthesizes evidence at unit level, and reconstructs a DOCX
research output.

## Pipeline Architecture

1. Preflight locks the source PDF identity, evidence window, model identifiers,
   and cost-control policy.
2. PDF extraction uses Gemini native-PDF extraction to recover source facts,
   chronology, recommendations, references, tables, and grading information.
3. Ontology and query construction derives HCC chapters, evidence units, and
   PubMed query registry entries from the source.
4. PubMed retrieval searches half-year date slices, records query/slice
   provenance, and fetches unique PMIDs once.
5. Evidence selection deterministically retains human RCTs, meta-analyses,
   systematic reviews, and other reviews while excluding guideline and
   consensus records.
6. Mapping and appraisal assigns selected evidence to HCC evidence units and
   appraises each PMID-unit assignment.
7. Targeted repair resolves missing or coverage-error mapping chunks without
   rerunning the full stage.
8. Stage A synthesis produces evidence-unit summaries from appraised evidence.
9. Stage B reconstruction writes chapter updates and generates the DOCX output
   and appendix.
10. QC verifies completeness, hashes, status files, and final artifact paths.

## Repository Structure

- `src/`: HCC runtime scripts.
- `config/`: placeholder-only runtime and pricing templates.
- `docs/CODE_MANIFEST.md`: code-only dependency and stage manifest.
- `tests/`: no-network smoke, CLI help, and repository-policy tests.
- `.env.example`: environment-variable names only.

Local run workspaces such as `data/`, `input/`, `output/`, `audit/`, `logs/`,
and `run_state/` are intentionally ignored by Git.

## Required Software

- Python 3.12 or newer.
- `uv`.
- Poppler tools for preflight PDF checks: `pdfinfo`, `pdftotext`, and
  `pdftoppm`.
- Authenticated provider accounts for stages that call Gemini, OpenAI, and
  NCBI.

## Installation

```bash
uv sync
```

## Environment Variables

Create a local `.env` or export variables in your shell. Do not commit real
values.

Required names used by the pipeline:

- `OPENAI_API_KEY`
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `NCBI_API_KEY`
- `NCBI_EMAIL`
- `NCBI_TOOL`

Optional configuration names:

- `OPENAI_MODEL`
- `HCC_ROOT`
- `HCC_SOURCE_PDF`
- `HCC_COST_MODE`
- `HCC_MAX_TOTAL_API_USD`
- `HCC_MAX_OPENAI_API_USD`
- `HCC_MAX_GEMINI_API_USD`

## Input PDF Configuration

Place the historical source PDF outside Git, for example:

```bash
export HCC_ROOT=/path/to/local/hcc-run-workspace
export HCC_SOURCE_PDF=/path/to/local/ESMOHCC2012.pdf
```

The source PDF must be the ESMO-ESDO HCC Clinical Practice Guideline 2012. Do
not place the PDF in the repository.

## Output Directory Configuration

The runtime writes generated data under `HCC_ROOT`, using subdirectories such as
`data/`, `audit/`, `logs/`, `run_state/`, and `output/`. Keep `HCC_ROOT`
outside the Git repository, or use an ignored local workspace.

## Commands

Preflight, no-network validation:

```bash
uv run python src/hcc_preflight_protocol.py \
  --hcc-root "$HCC_ROOT" \
  --pdf "$HCC_SOURCE_PDF" \
  --offline
```

Preflight for a real run, including provider-model inventory:

```bash
uv run python src/hcc_preflight_protocol.py \
  --hcc-root "$HCC_ROOT" \
  --pdf "$HCC_SOURCE_PDF" \
  --cost-mode LOCAL_PRICING_REQUIRED
```

PDF extraction:

```bash
uv run python src/hcc_gemini_extract_source.py --hcc-root "$HCC_ROOT"
uv run python src/hcc_gemini_repair_extraction.py --hcc-root "$HCC_ROOT"
```

Ontology and PubMed query registry:

```bash
uv run python src/hcc_build_ontology_queries.py --hcc-root "$HCC_ROOT"
```

PubMed retrieval:

```bash
uv run python src/hcc_pubmed_retrieve_unique.py --hcc-root "$HCC_ROOT"
```

Evidence selection:

```bash
uv run python src/hcc_select_evidence.py --hcc-root "$HCC_ROOT"
```

Mapping and evidence appraisal:

```bash
uv run python src/hcc_gpt_map_appraise_background.py --hcc-root "$HCC_ROOT"
uv run python src/hcc_repair_mapping_gaps.py --hcc-root "$HCC_ROOT"
uv run python src/hcc_build_integration_master.py --hcc-root "$HCC_ROOT"
```

Fallback mapping modes:

```bash
uv run python src/hcc_gpt_map_appraise_direct.py --hcc-root "$HCC_ROOT" --mode all
uv run python src/hcc_gpt_map_appraise_batch.py --hcc-root "$HCC_ROOT" --mode all
uv run python src/hcc_gpt_map_appraise_shards.py --hcc-root "$HCC_ROOT" --mode all
```

Stage A evidence synthesis:

```bash
uv run python src/hcc_synthesize_chunks_background.py --hcc-root "$HCC_ROOT"
uv run python src/hcc_synthesize_units.py --hcc-root "$HCC_ROOT" --mode all
```

Guideline reconstruction:

```bash
uv run python src/hcc_reconstruct_guideline_docx.py --hcc-root "$HCC_ROOT" --mode run
```

DOCX generation from completed Stage B JSONL:

```bash
uv run python src/hcc_reconstruct_guideline_docx.py --hcc-root "$HCC_ROOT" --mode docx
```

Resume:

```bash
uv run python src/hcc_gpt_map_appraise_background.py --hcc-root "$HCC_ROOT" --poll-only
uv run python src/hcc_synthesize_chunks_background.py --hcc-root "$HCC_ROOT" --poll-only
uv run python src/hcc_reconstruct_guideline_docx.py --hcc-root "$HCC_ROOT" --mode all
```

QC:

```bash
uv run python src/hcc_final_qc_report.py --hcc-root "$HCC_ROOT"
```

## Checkpointing And Repair

Long-running stages write JSON state under `run_state/` and provider outputs
under `data/`. Re-running the same script resumes from completed chunks when
state files are present.

Targeted repair scripts operate on missing or coverage-error items after the
main stage has produced partial output. They are intended to repair specific
gaps while preserving completed work and deterministic merge validation.

## Deterministic Validation

The deterministic stages validate local structure and counts without model
calls. Evidence selection uses fixed publication-type and title/abstract rules.
Merge stages validate coverage, duplicate PMID-unit assignments, missing PMIDs,
status counts, and required output files before downstream synthesis or DOCX
generation.

## Evidence Hierarchy

The pipeline retains:

- Randomized controlled trials.
- Meta-analyses.
- Systematic reviews.
- Other reviews.

Guideline, consensus, expert recommendation, society recommendation, position
statement, and similar guidance records are excluded before model mapping and
appraisal.

Appraisal labels:

- `MAIN_SYNTHESIS`: evidence can support the main unit synthesis and may support
  narrative or recommendation change.
- `CONTEXT_ONLY`: evidence is relevant context but should not drive a
  recommendation change by itself.
- `APPENDIX`: evidence is retained for transparency, background, or
  hypothesis-generating support.
- `REJECT`: evidence is not used for the unit because of scope, design,
  directness, endpoint, or other appraisal reasons.

## Data And Copyright Policy

Do not commit source guidelines, generated guideline documents, PubMed
abstracts, metadata datasets, raw XML, provider batch inputs or outputs, logs,
state files, PDFs, DOCX files, archives, or credentials. Source PDFs and
generated documents must be managed locally according to their copyright and
license terms.

## Reproducibility Limitations

External services can change model availability, model behavior, rate limits,
API schemas, PubMed indexing, and publication metadata. The repository locks the
evidence window and model identifiers used by the pipeline, but reproducibility
still depends on provider access, local source-PDF availability, PubMed state,
and expert review of generated research outputs.

## AI-Model Transparency

The locked HCC protocol uses:

- Gemini native-PDF extraction model: `models/gemini-3.5-flash`.
- OpenAI mapping, appraisal, synthesis, and reconstruction model:
  `gpt-5.6-sol`.

Provider responses and run manifests are generated artifacts and are not
distributed in this repository.

## Citation

Use `CITATION.cff` for software citation metadata. Cite the historical source
guideline separately according to the publisher's citation requirements.

## License Status

No open-source license is granted in this repository unless a license file is
added later by the copyright holder. All rights are reserved by default.

## Not Distributed

This repository does not distribute the ESMO-ESDO HCC 2012 source guideline,
any human-authored ESMO HCC benchmark guideline, generated guideline DOCX
outputs, PubMed datasets, provider payloads, or local run data.
