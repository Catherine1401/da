# Technology trends and developer salaries (Stack Overflow Developer Survey 2025)

Group project for the course CSE702060 – Data Visualization (Phenikaa School of Computing). The analysis, slides and report are written in Vietnamese.

## Deliverables

| File | Content |
|---|---|
| `deliverables/so2025.ipynb` | Executed notebook: 23 charts for 9 analysis questions |
| `deliverables/slides.pptx` | 12-slide presentation |
| `deliverables/report.docx` | Report (about 40 pages) |

## Repository layout

| Path | Content |
|---|---|
| `notebook/parts/` | Source of the notebook, split into cells-per-file parts (`00_setup` … `08_summary`) |
| `build/make_nb.py` | Assembles the parts into `deliverables/so2025.ipynb` and executes it |
| `build/build_pptx.py`, `build/build_docx.py` | Build the slides and the report from `out/` (charts, notes, tables) |
| `docs/` | Course lecture slides, meeting minutes, assignment intent |
| `plan.md`, `design.md` | Plan and chart catalogue |
| `requirements.txt` | Pinned Python dependencies (Python 3.10) |

## Run on another machine

Requirements: Python 3.10, git, and internet access (the raw data, about 141 MB, is downloaded automatically into `data/` on the first run).
Optional system tools: Google Chrome (plotly static image export; if missing run `.venv/bin/plotly_get_chrome`), LibreOffice and poppler-utils (page counting and the table of contents of the report).

```bash
git clone <repository-url> da && cd da
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

.venv/bin/python build/make_nb.py      # notebook -> deliverables/so2025.ipynb, charts -> out/
.venv/bin/python build/build_pptx.py   # slides   -> deliverables/slides.pptx
.venv/bin/python build/build_docx.py   # report   -> deliverables/report.docx
```

The slide and report scripts read only `out/`, so run `make_nb.py` first. All three scripts overwrite the files in `deliverables/`.

Autonomous agents: read `AGENTS.md` (setup, run, verification checklist, troubleshooting).
