# AGENTS.md

Instructions for an autonomous agent (or a new contributor) working in this repository.
Goal: from a fresh clone, set up, run, verify and modify the project without asking questions.

## What this project is

Course project (CSE702060 – Data Visualization): analysis of the Stack Overflow Developer Survey 2025 (technology trends and developer salaries). Three Vietnamese deliverables are produced from one source of truth:

| Deliverable | Path | Produced by |
|---|---|---|
| Executed notebook (23 charts) | `deliverables/so2025.ipynb` | `build/make_nb.py` |
| Slides (exactly 12) | `deliverables/slides.pptx` | `build/build_pptx.py` |
| Report (at least 30 pages, currently about 40) | `deliverables/report.docx` | `build/build_docx.py` |

## Data flow

```
notebook/parts/*.py ──make_nb.py──> deliverables/so2025.ipynb
                                └─> out/figs/*.png        (23 charts, 1600x900)
                                    out/tables/*.csv      (plotted tables)
                                    out/tables/f*_note.json (title, observation, insight, footer, n per chart)
                                    out/tables/summary.json (headline numbers and messages)
out/  ──build_pptx.py──> deliverables/slides.pptx
out/  ──build_docx.py──> deliverables/report.docx   (builds twice to fill the table of contents with page numbers)
```

`out/` and `data/` are git-ignored and are regenerated. The raw data (`data/results.csv`, 141 MB) is downloaded automatically by the notebook when missing.

## Prerequisites

| Need | Why | If missing |
|---|---|---|
| Python 3.10 | `requirements.txt` is pinned for 3.10 (other versions are untested) | install Python 3.10 |
| Internet access | first run downloads `data/results.csv` from `github.com/StackExchange/Survey` | download it manually to `data/results.csv` |
| Google Chrome | plotly static image export (treemap, Sankey, map, spider) through kaleido | `.venv/bin/plotly_get_chrome` |
| LibreOffice (`soffice`) and poppler (`pdftotext`) | `build_docx.py` converts to PDF to count pages and fill the table of contents | `apt install libreoffice poppler-utils` |

No display is needed; everything runs headless.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Always call scripts through `.venv/bin/python`. `make_nb.py` runs the notebook with the `python3` kernel of that virtual environment; running it with another interpreter fails with a missing-kernel or missing-module error.

## Run (in this order)

```bash
.venv/bin/python build/make_nb.py      # about 25-50 s (first run also downloads the data)
.venv/bin/python build/build_pptx.py   # a few seconds
.venv/bin/python build/build_docx.py   # about 1 min (LibreOffice runs twice)
```

`build_pptx.py` and `build_docx.py` read only `out/`, so `make_nb.py` must have run first. All three scripts overwrite `deliverables/`.

## Verify (all must hold)

1. `make_nb.py` ends with `Đã lưu .../so2025.ipynb (66 ô)`.
2. No error output and no unexecuted code cell:
   ```bash
   .venv/bin/python - <<'EOF'
   import nbformat
   nb = nbformat.read("deliverables/so2025.ipynb", 4)
   code = [c for c in nb.cells if c.cell_type == "code"]
   assert not [o for c in code for o in c.outputs if o.output_type == "error"]
   assert all(c.execution_count is not None for c in code)
   print("notebook ok", len(code), "code cells")
   EOF
   ```
3. `ls out/figs/*.png | wc -l` prints `23`; `ls out/tables/f*_note.json | wc -l` prints `23`.
4. `build_pptx.py` prints `(12 slide)`.
5. `build_docx.py` prints `N trang` with N >= 30 and `mục không tìm thấy số trang: 0` (it exits non-zero if fewer than 30 pages).
6. Headline numbers in `out/tables/summary.json` (these are fixed by the 2025 dataset and the cleaning rules):

   | Key | Expected |
   |---|---|
   | `n_all` | 49191 |
   | `n_sal` | 19576 |
   | `n_countries` | 62 |
   | `median_pay` | 79578 |
   | `vn_rank`, `vn_n` | 57, 31 |
   | `r2_country`, `r2_country_exp`, `r2_full` | about 0.4486, 0.5216, 0.5472 |

If a number differs, a cleaning rule or the data changed; do not patch the expected value, find the cause.

## Where to change things

| Task | Edit | Then re-run |
|---|---|---|
| Cleaning thresholds (salary range, minimum sample sizes, experience bins) | `Cfg` in `notebook/parts/00_setup.py` | all three scripts |
| A chart or its title/observation/insight | the `fig_*` function in the matching `notebook/parts/NN_*.py` | all three scripts |
| Report text, tables, figure order | `build/report_ch12.py`, `report_ch3.py`, `report_ch4.py`, `report_ch56.py` | `build_docx.py` |
| Slide layout and slide order | `build/build_pptx.py` | `build_pptx.py` |
| Report styling and helpers | `build/docx_kit.py`, `build/report_common.py` | `build_docx.py` |

Rules that keep the three deliverables consistent:

- Never edit `deliverables/` or `out/` by hand; they are generated.
- Never hard-code a number in report or slide text. Numbers come from `out/tables/*.csv`, `f*_note.json` and `summary.json`. In notebook notes, compute sentences from data (including conditional wording such as "increases" or "does not increase").
- Table and figure references in report text use `[[tab:key]]` and `[[fig:code]]`; they are resolved to numbers at build time.
- Every chart carries its sample size `n` and its filters in the footer, and its title states the finding.
- Wording must describe association ("goes together with"), never causation; the data are self-reported survey answers.

## Conventions

- Language: deliverables, notebook markdown and code comments are Vietnamese; this file, the README, commit messages and other repository documentation are English.
- Code comments are one line each. Files stay at or below 1000 lines and functions at or below 100 lines. Every literal that carries meaning is a named constant. Do not change any font.
- The notebook is intentionally a single self-contained `.ipynb` (course requirement), assembled from the files in `notebook/parts/`. The assembled code exceeds 1000 lines although every source file is far below it; keep new logic in small functions.
- Commits: `prefix(scope): imperative verb + concise object`, with `feat`, `fix`, `docs`, `refactor` or `chore`. One commit per independent task; stage only the hunks of that task.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `No such kernel named python3` or `ModuleNotFoundError` in `make_nb.py` | the script was started with the wrong interpreter; use `.venv/bin/python` |
| Error from `write_image` / kaleido about Chrome | install Chrome or run `.venv/bin/plotly_get_chrome` |
| `FileNotFoundError: soffice` or `pdftotext` in `build_docx.py` | install LibreOffice and poppler-utils |
| `out/tables/summary.json` not found in the slide/report scripts | run `make_nb.py` first |
| Data download fails or stalls | `mkdir -p data && curl -L -o data/results.csv "https://github.com/StackExchange/Survey/raw/refs/heads/main/packages/archive/2025/results.csv"` (do not commit it; it exceeds the 100 MB GitHub limit) |
| Report has a different page count in Word | page counts and the table of contents are measured with LibreOffice; Word may paginate slightly differently |
| `pip install` fails on a Python version other than 3.10 | the pins target 3.10; use 3.10 or relax the pins and re-verify the numbers above |
