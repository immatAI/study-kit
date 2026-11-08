#!/usr/bin/env python
"""Remove low-value / personal info / promo pages from extracted.md.

Default: drop pages containing promo/personal/boilerplate keywords, and redact
emails/phones in kept pages. Page numbers stay as original page markers, so
citations still point at the PDF.

Usage:
  python sanitize.py --dir <out> --drop-pages 1-3
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# Promo/personal/boilerplate markers. Keep this list specific; don't drop
# ordinary knowledge pages that merely mention a generic word like "course".
DROP_KEYWORDS = [
    "个人介绍", "讲师", "报名", "扫码", "二维码", "微信", "电话", "邮箱",
    "今晚", "试听", "客服", "价格", "公众号", "课程咨询", "联系我",
    "instructor", "contact", "email", "register", "promo", "course intro",
    "tuition", "price", "tonight",
]
REDACT_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[email]"),
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "[phone]"),
]


def parse_pages(spec: str) -> set[int]:
    pages: set[int] = set()
    if not spec:
        return pages
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            pages.update(range(int(a), int(b) + 1))
        else:
            pages.add(int(part))
    return pages


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--drop-pages", default="")
    ap.add_argument("--out-name", default="extracted.sanitized.md")
    args = ap.parse_args()

    root = Path(args.dir)
    src = root / "extracted.md"
    if not src.exists():
        raise SystemExit(f"missing {src}")
    text = src.read_text(encoding="utf-8")
    parts = re.split(r"\n## Page (\d+)\n", text)
    drop = parse_pages(args.drop_pages)
    kept = []
    report = {"source": str(src), "dropped": [], "redactions": {}, "kept_pages": 0}
    redactions = {p.pattern: 0 for p, _ in REDACT_PATTERNS}

    for i in range(1, len(parts), 2):
        num = int(parts[i])
        body = parts[i + 1]
        body_l = body.lower()
        hits = [k for k in DROP_KEYWORDS if k.lower() in body_l]
        reason = ""
        if num in drop:
            reason = "requested"
        elif hits:
            reason = "keyword:" + ",".join(hits)
        if reason:
            report["dropped"].append({"page": num, "reason": reason})
            continue
        for pattern, repl in REDACT_PATTERNS:
            body, n = pattern.subn(repl, body)
            if n:
                redactions[pattern.pattern] += n
        kept.append(f"\n## Page {num}\n{body.rstrip()}\n")
        report["kept_pages"] += 1

    report["redactions"] = {k: v for k, v in redactions.items() if v}
    (root / args.out_name).write_text("".join(kept), encoding="utf-8")
    (root / "sanitize-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"kept_pages": report["kept_pages"], "dropped": report["dropped"], "redactions": report["redactions"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
