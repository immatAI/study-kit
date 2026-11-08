#!/usr/bin/env python
"""Step 3: assemble manifest + OCR .txt files into extracted.md."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    args = ap.parse_args()
    outdir = Path(args.dir)
    data = json.loads((outdir / "manifest.json").read_text(encoding="utf-8"))
    sections = []
    text_chars = 0
    ocr_chars = 0
    ocr_pages = 0
    for item in data["pages"]:
        text = item.get("text", "")
        ocr = ""
        if item.get("image"):
            p = outdir / (item["image"] + ".txt")
            if p.exists():
                ocr = p.read_text(encoding="utf-8", errors="replace").strip()
        text_chars += len(text)
        ocr_chars += len(ocr)
        if ocr:
            ocr_pages += 1
        sections.append(f"\n## Page {item['page']}\n\n### Text\n{text or '（无）'}\n\n### OCR\n{ocr or '（无）'}\n")
    (outdir / "extracted.md").write_text("".join(sections), encoding="utf-8")
    stats = {"pdf": data["pdf"], "pages": len(data["pages"]), "text_chars": text_chars, "ocr_chars": ocr_chars, "ocr_pages": ocr_pages}
    (outdir / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
