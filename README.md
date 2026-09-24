# Intelligent Khata Extraction

LangGraph-orchestrated pipeline that turns a noisy handwritten Kannada+English property document into a structured `KhataRecord` JSON and a row in MySQL.

## Pipeline

```
Image
  → multi-pass Vision OCR (original + CLAHE)
  → text blob builder (proximity grouping, word→blob)
  → layout graph (right_of, below, aligned spatial relations — plain dict)
  → zone segmentation (HoughLinesP → header / table / footer)
  → header detection (heuristic + LLM canonical mapping → schema registry)
  → candidate generation (spatially connected blobs per header)
  → LLM field mapping + OCR correction (gpt-4o-mini, structured outputs)
  → translation validation (Google Translate + LLM check)
  → confidence scoring + retry loop (expand context if low conf)
  → stamp detection (HoughCircles + blob merge)
  → persist (MySQL property_records + property_dynamic_fields + raw_extractions + stamps)
```

## Setup

```bash
cd /Users/nityareddy/Desktop/IntelligentKhataExtractionOG
python3 -m venv .venv && source .venv/bin/activate
.venv/bin/python -m pip install -e .
```

Edit `.env`:
- `OPENAI_API_KEY` — rotate the key you previously shared
- `GOOGLE_APPLICATION_CREDENTIALS` — path to GCP service-account JSON
- MySQL credentials (defaults match local root/project@123)

## Initialize MySQL

```bash
.venv/bin/python scripts/init_db.py
```

## Run

```bash
.venv/bin/python main.py /Users/nityareddy/Desktop/CS/projects/MINI_PROJECT/khata/2.png
```

Outputs land in `data/output/<document_id>/`:
- `blobs.json` — text blobs with bboxes
- `layout_graph.json` — spatial adjacency
- `zones.json` — header/table/footer
- `headers.json` — detected headers + canonical mapping
- `candidates.json` — candidates per header
- `khata_record.json` — final structured record

## Schema registry

`data/schema_registry.json` accumulates `{label → canonical_field}` mappings from prior LLM calls so repeat labels skip the LLM. Persisted across runs.
