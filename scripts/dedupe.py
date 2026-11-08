#!/usr/bin/env python
"""Lightweight dedupe check: compare draft pages against existing Markdown pages.

Not semantic search; it uses token overlap as a cheap first pass. The draft is
split by `## Page N` markers so a matching page can be flagged even when the
whole draft contains unrelated pages.

Usage:
  python dedupe.py --draft demo/out/extracted.sanitized.md --existing demo/existing
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def tokens(text: str) -> set[str]:
    text = text.lower()
    en = set(re.findall(r"[a-z0-9_]{2,}", text))
    cjk = set(re.findall(r"[\u4e00-\u9fff]{2}", text))
    return en | cjk


def headings(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"^#{1,6}\s+(.+)$", text, re.M)}


def collect(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(p for p in path.rglob("*.md") if p.is_file())
    return [path] if path.is_file() else []


def split_pages(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"^## Page (\d+)\s*$", text, flags=re.M)
    if len(parts) <= 1:
        return [("document", text)]
    pages = []
    for i in range(1, len(parts), 2):
        pages.append((f"page {parts[i]}", parts[i + 1]))
    return pages


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--existing", required=True)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    draft_text = Path(args.draft).read_text(encoding="utf-8", errors="replace")
    existing = [(p, p.read_text(encoding="utf-8", errors="replace")) for p in collect(Path(args.existing))]
    results = []
    for page, body in split_pages(draft_text):
        d_tokens = tokens(body)
        d_heads = headings(body)
        if not d_tokens:
            continue
        best = None
        for path, text in existing:
            e_tokens = tokens(text)
            inter = d_tokens & e_tokens
            union = d_tokens | e_tokens
            score = len(inter) / len(union) if union else 0.0
            cand = {
                "page": page,
                "path": str(path),
                "score": round(score, 3),
                "shared_headings": sorted(d_heads & headings(text))[:5],
                "shared_terms": sorted(inter)[:10],
            }
            if best is None or cand["score"] > best["score"]:
                best = cand
        if best:
            best["decision"] = "likely-duplicate" if best["score"] >= 0.30 else "new"
            results.append(best)

    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[: args.limit]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['page']:8} {r['decision']:16} {r['score']:.3f}  {r['path']}")
            if r["shared_headings"]:
                print("  headings:", ", ".join(r["shared_headings"]))
            if r["shared_terms"]:
                print("  terms:   ", ", ".join(r["shared_terms"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
