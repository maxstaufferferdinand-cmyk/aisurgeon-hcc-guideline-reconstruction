# HCC Code Manifest

This manifest lists tracked runtime code only. It does not contain scientific
result data, run manifests, model outputs, PubMed records, or generated
guideline text.

| Runtime script | Pipeline stage | Purpose | Direct local dependencies |
| --- | --- | --- | --- |
| `src/hcc_preflight_protocol.py` | Preflight | Validate the source PDF, lock the evidence window and model identifiers, initialize protocol and cost-control artifacts. | none |
| `src/hcc_gemini_extract_source.py` | PDF extraction | Submit the 2012 source PDF to Gemini native-PDF extraction and write structured source-context artifacts. | none |
| `src/hcc_gemini_repair_extraction.py` | PDF extraction repair | Run targeted Gemini repair for source chronology/extraction gaps. | none |
| `src/hcc_build_ontology_queries.py` | Ontology and search setup | Build the source-derived HCC evidence-unit ontology and PubMed query registry. | none |
| `src/hcc_pubmed_retrieve.py` | PubMed retrieval | Retrieve PubMed results by query and half-year date slice with resumable state. | none |
| `src/hcc_pubmed_retrieve_unique.py` | PubMed retrieval | Collect query/slice PMID provenance and fetch each unique PMID once. | `hcc_pubmed_retrieve.py` |
| `src/hcc_select_evidence.py` | Evidence selection | Deterministically classify, exclude guidance/consensus records, and select target evidence types. | none |
| `src/hcc_gpt_map_appraise_batch.py` | Mapping and appraisal | Prepare, submit, watch, and merge OpenAI Batch mapping/appraisal work. | none |
| `src/hcc_gpt_map_appraise_shards.py` | Mapping and appraisal | Split mapping/appraisal work into multiple batch shards. | `hcc_gpt_map_appraise_batch.py` |
| `src/hcc_gpt_map_appraise_direct.py` | Mapping and appraisal fallback | Run direct resumable OpenAI Responses mapping/appraisal chunks. | `hcc_gpt_map_appraise_batch.py` |
| `src/hcc_gpt_map_appraise_background.py` | Mapping and appraisal fallback | Submit and poll background Responses mapping/appraisal chunks. | `hcc_gpt_map_appraise_batch.py`, `hcc_gpt_map_appraise_direct.py` |
| `src/hcc_repair_mapping_gaps.py` | Targeted repair | Repair missing mapping/appraisal PMIDs after background or direct runs. | `hcc_gpt_map_appraise_batch.py`, `hcc_gpt_map_appraise_direct.py` |
| `src/hcc_build_integration_master.py` | Integration master | Freeze the final ontology and build the unit-wise integration master. | none |
| `src/hcc_synthesize_chunks_background.py` | Stage A evidence synthesis | Submit and poll background chunk-level evidence synthesis jobs. | `hcc_gpt_map_appraise_background.py`, `hcc_gpt_map_appraise_batch.py`, `hcc_gpt_map_appraise_direct.py`, `hcc_synthesize_units.py` |
| `src/hcc_synthesize_units.py` | Stage A evidence synthesis | Run and merge final evidence-unit reducers. | `hcc_gpt_map_appraise_batch.py`, `hcc_gpt_map_appraise_direct.py` |
| `src/hcc_reconstruct_guideline_docx.py` | Stage B reconstruction and DOCX | Reconstruct chapters from Stage A synthesis and generate DOCX plus appendix. | `hcc_gpt_map_appraise_batch.py`, `hcc_gpt_map_appraise_direct.py` |
| `src/hcc_final_qc_report.py` | Final QC | Verify final artifacts, hashes, counts, and local git state for a run workspace. | none |

## Non-Runtime Validation Code

| File | Purpose |
| --- | --- |
| `tests/test_smoke_imports.py` | Syntax and import smoke tests for tracked Python scripts without network calls. |
| `tests/test_cli_help.py` | Verifies each runtime CLI exposes `--help` without calling external services. |
| `tests/test_repository_policy.py` | Checks placeholder configuration, prohibited artifact extensions, local-path leakage, and obvious secret-like values. |
