# Study Kit (prototype)

> [Release v0.1.1](https://github.com/immatAI/study-kit/releases/tag/v0.1.1) · [Landing page](https://immatAI.github.io/study-kit/) · [中文介绍](https://zhuanlan.zhihu.com/p/2102890902192664583) · ![ci](https://github.com/immatAI/study-kit/actions/workflows/ci.yml/badge.svg)

> **Turn image-only PDFs into sanitized, traceable Markdown notes — locally, no external API.**
> 把图片型 PDF 变成“可检索、已清洗、可核对”的 Markdown 笔记；只在本机跑，不调用外部模型。

## Why

- 很多扫描件/截图资料是 **图片 PDF**：pypdf 抽不出文字，直接丢给模型又贵、又容易把无价值页和敏感信息带进知识库。
- 现有工具通常只做“OCR”或“总结”，很少把 **清洗、去重、审批回执** 串起来。
- Study Kit 的目标：本地 OCR → 规则清洗（无价值页/敏感信息）→ Markdown → 审批回执；全程可核对。

## Status

**Prototype / P1 done + P2 public**：抽图 + Windows OCR + 规则清洗 + 合成 demo；回执、去重、冒烟测试、CLI、DSH skill 已可用；已发布 GitHub / Release / Pages。

Demo 实测：3 页合成 PDF，第 1 页（封面/联系页）被清洗，保留 2 页知识页；OCR 文本有错字，符合预期。

## Receipt (approval)

```powershell
python scripts\receipt.py approve --dir demo\out --by reviewer
python scripts\receipt.py verify  --dir demo\out
```

回执记录源 PDF 哈希、清洗后 Markdown 哈希、清洗报告哈希、批准人、时间、前序哈希；`verify` 会重算并检查链。

## Dedupe

```powershell
python scripts\dedupe.py --draft demo\out\extracted.sanitized.md `
  --existing demo\existing --json
```

按 `## Page N` 分页，与已有 Markdown 做 token 重叠；输出 `likely-duplicate` / `new`。它是廉价初筛，不是语义检索。

## Smoke test

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tests\smoke.ps1
```

覆盖：pipeline → 丢无关页 → approve → verify → 篡改检测 → dedupe。

## Quick start

```powershell
# one entry point (run / approve / verify / dedupe)
.\study-kit.ps1 run -Pdf demo\slides.pdf -Out demo\out -DropPages 1
.\study-kit.ps1 approve --dir demo\out --by reviewer
.\study-kit.ps1 verify  --dir demo\out
.\study-kit.ps1 dedupe  --draft demo\out\extracted.sanitized.md --existing demo\existing
```

Or call the scripts directly (same commands as below).

## DSH skill

`.\dsh\skills\study-kit\SKILL.md` 是同一套脚本的 DSH skill 入口；复制到自己的 `.dsh/skills/` 即可用。

## Demo (synthetic)

```powershell
# 1) 生成 3 页合成 PDF（第 1 页是封面/联系页，应被清洗）
python demo\make_demo.py

# 2) 跑本地流水线，显式丢弃第 1 页
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run.ps1 `
  -Pdf demo\slides.pdf -Out demo\out -DropPages 1
```

输出：

```text
demo/out/
├── extracted.sanitized.md   # 只留知识页，已清洗
├── sanitize-report.json     # 丢了哪些页、脱敏了什么
├── stats.json
├── receipt.approved.json    # approve 后生成
└── receipts.jsonl           # 回执链
```

## Requirements

- Windows 10/11（当前 OCR 依赖 `Windows.Media.Ocr`）。
- Python 3.11+；`pip install -r requirements.txt`（`pypdf`；`Pillow` 只用于生成合成 demo）。
- 设置 `STUDY_KIT_PYTHON` 指向装了依赖的解释器，或让 `python` 在 PATH 中。
- 不联网；不上传任何文档。

## Limitations

- 只 OCR 每页最大图；一页多图可能漏内容。
- OCR 有错字/空格/大小写问题，公式/表格/结构图要回看原 PDF。
- 规则清洗不能保证 100% 去除敏感信息；高风险资料仍需人工复核。
- 仍是 prototype，接口可能变化；当前离线 OCR 仅支持 Windows。

## Next

- 跨平台 OCR backend（macOS/Linux）。
- 可配置的清洗规则（YAML）。
- DSH 市场/技能上架；按真实反馈决定优先级。

指标：5 次有效对话，或 30–100 stars，或 1 个合作线索；无信号就保持本地工具。

## Data handling

- 全程本地处理；demo 使用合成数据。
- 清洗阶段移除无价值页和敏感信息；高风险资料仍需人工复核。
