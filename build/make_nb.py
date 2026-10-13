"""Ghép các phần trong notebook/parts thành deliverables/so2025.ipynb rồi chạy để có sẵn kết quả."""
import sys
from dataclasses import dataclass
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
PARTS_DIR = ROOT / "notebook" / "parts"
OUT_NB = ROOT / "deliverables" / "so2025.ipynb"
CELL_MARK = "# %%"
MARKDOWN_MARK = "# %% [markdown]"
RUN_KERNEL = "python3"
RUN_TIMEOUT = 1800
NO_EXEC_FLAG = "--no-exec"
SAVED_KERNEL = {"name": "python3", "display_name": "Python 3", "language": "python"}


@dataclass(frozen=True)
class Cell:
    """Một ô của notebook: loại và nội dung."""
    kind: str
    source: str


def clean_markdown(lines: list) -> str:
    """Bỏ tiền tố '# ' của các dòng markdown."""
    return "\n".join(line[2:] if line.startswith("# ") else line.lstrip("#") for line in lines).strip()


def split_cells(text: str) -> list:
    """Tách nội dung một file phần thành các ô theo dấu '# %%'."""
    cells, kind, lines = [], None, []
    for line in text.splitlines():
        if line.startswith(CELL_MARK):
            if kind is not None:
                cells.append(close_cell(kind, lines))
            kind, lines = ("markdown" if line.strip() == MARKDOWN_MARK else "code"), []
        else:
            lines.append(line)
    if kind is not None:
        cells.append(close_cell(kind, lines))
    return [cell for cell in cells if cell.source]


def close_cell(kind: str, lines: list) -> Cell:
    """Hoàn tất một ô: markdown thì bỏ tiền tố, code thì cắt dòng trống đầu cuối."""
    source = clean_markdown(lines) if kind == "markdown" else "\n".join(lines).strip("\n")
    return Cell(kind, source)


def build_notebook() -> nbformat.NotebookNode:
    """Dựng notebook từ mọi file phần theo thứ tự tên."""
    notebook = nbformat.v4.new_notebook()
    for path in sorted(PARTS_DIR.glob("*.py")):
        for cell in split_cells(path.read_text(encoding="utf-8")):
            make = nbformat.v4.new_markdown_cell if cell.kind == "markdown" else nbformat.v4.new_code_cell
            notebook.cells.append(make(cell.source))
    return notebook


def execute(notebook: nbformat.NotebookNode) -> None:
    """Chạy toàn bộ notebook từ đầu với thư mục gốc dự án làm thư mục làm việc."""
    client = NotebookClient(notebook, timeout=RUN_TIMEOUT, kernel_name=RUN_KERNEL, resources={"metadata": {"path": str(ROOT)}})
    client.execute()
    notebook.metadata["kernelspec"] = SAVED_KERNEL


def main(argv: list) -> None:
    """Điểm vào: ghép, chạy (trừ khi có --no-exec) và lưu."""
    notebook = build_notebook()
    if NO_EXEC_FLAG not in argv:
        execute(notebook)
    OUT_NB.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, OUT_NB)
    print(f"Đã lưu {OUT_NB} ({len(notebook.cells)} ô)")


if __name__ == "__main__":
    main(sys.argv[1:])
