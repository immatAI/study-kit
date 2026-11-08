#!/usr/bin/env python
"""Approval receipt for a sanitized run.

Receipt fields: source/pdf hash, sanitized markdown hash, sanitize report hash,
approver, timestamp, previous receipt hash, and this receipt hash.

Usage:
  python receipt.py approve --dir demo/out --by reviewer
  python receipt.py verify  --dir demo/out
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ = timezone(timedelta(hours=8))


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(obj: dict) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def receipt_hash(obj: dict) -> str:
    payload = {k: v for k, v in obj.items() if k != "hash"}
    return hashlib.sha256(canonical(payload)).hexdigest()


def last_hash(ledger: Path) -> str:
    if not ledger.exists():
        return "GENESIS"
    lines = [ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        return "GENESIS"
    return json.loads(lines[-1])["hash"]


def load_run(out: Path) -> tuple[Path, Path, Path, Path]:
    sanitized = out / "extracted.sanitized.md"
    report = out / "sanitize-report.json"
    stats = out / "stats.json"
    if not sanitized.exists() or not report.exists() or not stats.exists():
        raise SystemExit(f"missing run files under {out} (run the pipeline first)")
    meta = json.loads(stats.read_text(encoding="utf-8"))
    source = Path(meta["pdf"])
    if not source.is_absolute():
        source = (Path.cwd() / source).resolve()
    if not source.exists():
        raise SystemExit(f"source pdf not found: {source}")
    return source, sanitized, report, stats


def cmd_approve(args) -> int:
    out = Path(args.dir).resolve()
    source, sanitized, report, stats = load_run(out)
    ledger = Path(args.ledger).resolve() if args.ledger else (out / "receipts.jsonl")
    payload = {
        "run": out.name,
        "source": str(source),
        "source_sha256": sha256(source),
        "sanitized": str(sanitized),
        "sanitized_sha256": sha256(sanitized),
        "sanitize_report": str(report),
        "sanitize_report_sha256": sha256(report),
        "approved_by": args.by,
        "approved_at": now(),
        "prev_hash": last_hash(ledger),
    }
    payload["hash"] = receipt_hash(payload)
    (out / "receipt.approved.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
    print("approved:", out.name, "by", args.by)
    print("receipt:", payload["hash"])
    print("prev:   ", payload["prev_hash"])
    return 0


def cmd_verify(args) -> int:
    out = Path(args.dir).resolve()
    receipt_path = out / "receipt.approved.json"
    if not receipt_path.exists():
        raise SystemExit("no receipt.approved.json")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    ledger = Path(args.ledger).resolve() if args.ledger else (out / "receipts.jsonl")
    ok = True

    for key, path in (
        ("source_sha256", Path(receipt["source"])),
        ("sanitized_sha256", Path(receipt["sanitized"])),
        ("sanitize_report_sha256", Path(receipt["sanitize_report"])),
    ):
        actual = sha256(path) if path.exists() else "<missing>"
        if actual != receipt[key]:
            print(f"FAIL {key}: expected {receipt[key]} got {actual}")
            ok = False

    if receipt_hash(receipt) != receipt["hash"]:
        print("FAIL receipt hash mismatch")
        ok = False

    prev = "GENESIS"
    seen = False
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj["prev_hash"] != prev:
            print("FAIL chain broken at", obj.get("run"))
            ok = False
        if receipt_hash(obj) != obj["hash"]:
            print("FAIL chain entry tampered at", obj.get("run"))
            ok = False
        if obj.get("hash") == receipt["hash"]:
            seen = True
        prev = obj["hash"]
    if not seen:
        print("FAIL receipt not found in ledger")
        ok = False

    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("approve")
    a.add_argument("--dir", required=True)
    a.add_argument("--by", default="reviewer")
    a.add_argument("--ledger")
    a.set_defaults(func=cmd_approve)
    v = sub.add_parser("verify")
    v.add_argument("--dir", required=True)
    v.add_argument("--ledger")
    v.set_defaults(func=cmd_verify)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
