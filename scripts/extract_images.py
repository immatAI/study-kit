#!/usr/bin/env python
"""Step 1: extract pypdf text + candidate slide images into a manifest.

No OCR here. OCR is done by ocr_batch.ps1 in a PowerShell process (WinRT OCR
does not work reliably from a Python-spawned PowerShell on this machine).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from pypdf import PdfReader


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-pages", type=int, default=0)
    ap.add_argument("--min-area", type=int, default=300000)
    args = ap.parse_args()

    pdf = Path(args.pdf)
    outdir = Path(args.out)
    imdir = outdir / "images"
    imdir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(pdf))
    pages = reader.pages[: args.max_pages] if args.max_pages else reader.pages
    manifest = []
    for i, page in enumerate(pages, 1):
        text = (page.extract_text() or "").strip()
        xo = page.get("/Resources", {}).get("/XObject")
        images = []
        if xo:
            try:
                xo = xo.get_object()
                for key, ref in xo.items():
                    obj = ref.get_object()
                    if obj.get("/Subtype") != "/Image":
                        continue
                    w = int(obj.get("/Width", 0) or 0)
                    h = int(obj.get("/Height", 0) or 0)
                    images.append((w * h, w, h, key, obj))
            except Exception:
                pass
        images.sort(reverse=True, key=lambda x: x[0])
        image_rel = ""
        if images:
            area, w, h, key, obj = images[0]
            if area >= args.min_area and (len(text) < 120 or area > 1500000):
                try:
                    data = obj.get_data()
                    header = data[:2].hex()
                    ext = ".jpg" if header == "ffd8" else (".png" if header == "8950" else "")
                    if ext:
                        name = f"p{i:03d}{ext}"
                        (imdir / name).write_bytes(data)
                        image_rel = f"images/{name}"
                except Exception:
                    pass
        manifest.append({"page": i, "text": text, "image": image_rel, "image_area": images[0][0] if images else 0})

    (outdir / "manifest.json").write_text(json.dumps({"pdf": str(pdf), "pages": manifest}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pdf": str(pdf), "pages": len(manifest), "with_image": sum(1 for m in manifest if m["image"]), "text_chars": sum(len(m["text"]) for m in manifest)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
