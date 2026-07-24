"""Build the final thesis paper as one Word file.

Concatenates, in order: abstract, Ch1 introduction, Ch2 RRL, Ch3 technical
background, Ch4 methodology, the SRS, the non-letter appendices (expert-panel
rating form), and the bibliography — transmittal letters are excluded. Each part
starts on a new page.

Output format (post-processed into the docx): Arial 12 for all text, 1.5 line
spacing, A4, 1-inch margins except a 1.5-inch left margin, and no bookmark
anchors on headings.

Usage:  python to_final_docx.py        (requires Pandoc; stdlib only otherwise)
Output: Final Paper.docx at the repo root.
"""
import os
import re
import subprocess
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "Final Paper.docx")

PARTS = [
    "chapters/00-abstract/draft.md",
    "chapters/01-introduction/draft.md",
    "chapters/02-review-of-related-literature/draft.md",
    "chapters/03-technical-background/draft.md",
    "chapters/04-methodology/draft.md",
    "chapters/appendices/srs/SRS.md",
    "chapters/appendices/srs/Expert Panel Rating Form.md",
    "chapters/07-bibliography/draft.md",
]

PAGEBREAK = (
    '\n\n```{=openxml}\n'
    '<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n'
    '```\n\n'
)


def build_markdown():
    chunks = []
    for rel in PARTS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            raise SystemExit(f"missing part: {rel}")
        text = open(path, encoding="utf-8").read()
        # image paths are relative to each part's folder; the build runs from
        # the repo root, so point them all at assets/ directly
        text = text.replace("](../../../assets/", "](assets/")
        text = text.replace("](../../assets/", "](assets/")
        chunks.append(text.strip() + "\n")
    return PAGEBREAK.join(chunks)


def postprocess(docx_path):
    """Rewrite styles and layout inside the docx (stdlib zipfile only)."""
    with zipfile.ZipFile(docx_path) as z:
        items = {n: z.read(n) for n in z.namelist()}

    doc = items["word/document.xml"].decode("utf-8")
    # no bookmark anchors on headings
    doc = re.sub(r"<w:bookmark(Start|End)[^>]*/>", "", doc)
    # A4, 1-inch margins, 1.5-inch left (twips: 1440 = 1in); pandoc's sectPr
    # carries no page geometry, so inject it
    doc = re.sub(r"<w:pgSz[^>]*/>|<w:pgMar[^>]*/>", "", doc)
    doc = doc.replace(
        "</w:sectPr>",
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="2160" '
        'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>',
    )
    items["word/document.xml"] = doc.encode("utf-8")

    sty = items["word/styles.xml"].decode("utf-8")
    # every style: Arial, 12 pt (24 half-points), plain black; theme-font
    # references would fall back to Calibri/Cambria, so pin them too
    sty = re.sub(r'w:ascii="[^"]*"', 'w:ascii="Arial"', sty)
    sty = re.sub(r'w:hAnsi="[^"]*"', 'w:hAnsi="Arial"', sty)
    sty = re.sub(r'w:cs="[^"]*"', 'w:cs="Arial"', sty)
    sty = re.sub(r'w:asciiTheme="[^"]*"', 'w:ascii="Arial"', sty)
    sty = re.sub(r'w:hAnsiTheme="[^"]*"', 'w:hAnsi="Arial"', sty)
    sty = re.sub(r'w:cstheme="[^"]*"', 'w:cs="Arial"', sty)
    sty = re.sub(r"<w:sz\b[^>]*/>", '<w:sz w:val="24"/>', sty)
    sty = re.sub(r"<w:szCs\b[^>]*/>", '<w:szCs w:val="24"/>', sty)

    # headings: bold at every level (same 12 pt size, so bold is what
    # distinguishes them)
    def _embolden(m):
        block = re.sub(r'<w:bC?s?\s+w:val="0"\s*/>', "", m.group(0))
        if "<w:b/>" not in block and "<w:b />" not in block:
            if "<w:rPr>" in block:
                block = block.replace("<w:rPr>", "<w:rPr><w:b/><w:bCs/>", 1)
            else:
                block = block.replace(
                    "</w:style>", "<w:rPr><w:b/><w:bCs/></w:rPr></w:style>")
        return block

    sty = re.sub(r'<w:style [^>]*w:styleId="Heading[1-6]".*?</w:style>',
                 _embolden, sty, flags=re.S)
    sty = re.sub(r"<w:color[^>]*/>", '<w:color w:val="000000"/>', sty)
    # 1.5 line spacing: set the document default, and force it onto any style
    # that declares its own spacing without a line value
    sty = re.sub(
        r"(<w:docDefaults><w:pPrDefault><w:pPr>)(<w:spacing[^>]*/>)?",
        r'\1<w:spacing w:after="160" w:line="360" w:lineRule="auto"/>',
        sty,
        count=1,
    )
    sty = re.sub(
        r"<w:spacing((?:(?!w:line=)[^>])*)/>",
        r'<w:spacing\1 w:line="360" w:lineRule="auto"/>',
        sty,
    )
    items["word/styles.xml"] = sty.encode("utf-8")

    with zipfile.ZipFile(docx_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items.items():
            z.writestr(name, data)


def main():
    tmp = os.path.join(ROOT, "_final_paper_build.md")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(build_markdown())
    try:
        subprocess.run(
            ["pandoc", tmp, "-o", OUT, "--mathml"], cwd=ROOT, check=True
        )
    finally:
        os.remove(tmp)
    postprocess(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
