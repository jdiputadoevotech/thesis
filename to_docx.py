#!/usr/bin/env python3
"""Convert a chapter's draft.md to draft.docx. Usage: python to_docx.py chapters/03-technical-background"""
import subprocess, sys
from pathlib import Path

d = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
md = d / "draft.md"
# cwd=d so relative image paths (../../assets/...) resolve; --mathml -> native Word equations
subprocess.run(["pandoc", "draft.md", "-o", "draft.docx", "--mathml"], cwd=d, check=True)
print(f"wrote {md.with_name('draft.docx')}")
