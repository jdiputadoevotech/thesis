#!/usr/bin/env python3
"""Build the SRS as a standalone Word file.

Runs Pandoc on chapters/appendices/srs/SRS.md and applies the same formatting
pass as the final paper (Arial 12, 1.5 spacing, A4, 1.5-inch left margin, APA
tables/figures, no bookmarks). The thesis-level "APPENDIX A" heading is dropped
for the standalone document.

Usage:  python to_srs_docx.py
Output: chapters/appendices/srs/SRS.docx
"""
import os
import subprocess

from to_final_docx import postprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
SRS_DIR = os.path.join(ROOT, "chapters", "appendices", "srs")
OUT = os.path.join(SRS_DIR, "SRS.docx")


def main():
    text = open(os.path.join(SRS_DIR, "SRS.md"), encoding="utf-8").read()
    text = text.replace("# APPENDIX A\n\n", "", 1)
    tmp = os.path.join(SRS_DIR, "_srs_build.md")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    try:
        # cwd=SRS_DIR so the wireframe's relative image path resolves
        subprocess.run(["pandoc", "_srs_build.md", "-o", "SRS.docx",
                        "--mathml"], cwd=SRS_DIR, check=True)
    finally:
        os.remove(tmp)
    postprocess(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
