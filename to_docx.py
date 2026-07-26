#!/usr/bin/env python3
"""Convert a chapter's draft.md to draft.docx. Usage: python to_docx.py chapters/03-technical-background"""
import subprocess, sys, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from to_final_docx import apa_document, apa_styles

d = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
out = d / "draft.docx"
# cwd=d so relative image paths (../../assets/...) resolve; --mathml -> native Word equations
subprocess.run(["pandoc", "draft.md", "-o", "draft.docx", "--mathml"], cwd=d, check=True)

# APA 7 pass shared with the final-paper builder: horizontal-only table
# borders, alt-text captions stripped, figure captions kept with their image
with zipfile.ZipFile(out) as z:
    items = {n: z.read(n) for n in z.namelist()}
items["word/document.xml"] = apa_document(
    items["word/document.xml"].decode("utf-8")).encode("utf-8")
items["word/styles.xml"] = apa_styles(
    items["word/styles.xml"].decode("utf-8")).encode("utf-8")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for name, data in items.items():
        z.writestr(name, data)
print(f"wrote {out}")
