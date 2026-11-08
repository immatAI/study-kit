# Study Kit (prototype)

> [Release v0.1.0](https://github.com/immatAI/study-kit/releases/tag/v0.1.0) · ![ci](https://github.com/immatAI/study-kit/actions/workflows/ci.yml/badge.svg)

> **Turn image-only PDFs into sanitized, traceable Markdown notes — locally, no external API.**
> 把图片型 PDF 变成“可检索、已清洗、可核对”的 Markdown 笔记；只在本机跑，不调用外部模型。

## Why

- 很多课程/扫描资料是 **图片 PDF**：pypdf 抽不出文字，直接丢给模型又贵、又容易把个人信息/课程营销带进知识库。
- 现有工具通常只做“OCR”或“总结”，很少把 **清洗、去重、审批回执** 串起来。
- Study Kit 的目标：本地 OCR → 规则清洗（课程介绍/个人信息/推广页）→ Markdown → 审批回执；全程可核对。

## Status

**P0 done + P1 partial**：抽图 + Windows OCR + 规则清洗 + 合成 PDF demo；审批回执、去重、冒烟测试已可用。
P1 剩余：打包、去本机路径/特定 venv、错误处理；P2 才考虑公开。

Demo 实测：3 页合成 PDF，第 1 页（课程介绍/联系人）被清洗，保留 2 页知识页；OCR 文本有错字，符合预期。

## Receipt (approval)

```powershell
python scripts\receipt.py approve --dir demo\out-keywords --by reviewer
python scripts\receipt.py verify  --dir demo\out-keywords
```

回执记录源 PDF 哈希、清洗后 Markdown 哈希、清洗报告哈希、批准人、时间、前序哈希；`verify` 会重算并检查链。

## Dedupe

```powershell
python scripts\dedupe.py --draft demo\out-keywords\extracted.sanitized.md `
  --existing demo\existing --json
```

按 `## Page N` 分页，与已有 Markdown 做 token 重叠；输出 `likely-duplicate` / `new`。它是廉价初筛，不是语义检索。

## Smoke test

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tests\smoke.ps1
```

覆盖：pipeline → 丢课程页 → approve → verify → 篡改检测 → dedupe。

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
# 1) 生成 3 页合成 PDF（第 1 页是课程介绍/联系人，应被清洗）
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
└── stats.json
```

## Requirements

- Windows 10/11（当前 OCR 依赖 `Windows.Media.Ocr`）。
- Python 3.11+；`pip install -r requirements.txt`（`pypdf`；`Pillow` 只用于生成合成 demo）。
- 设置 `STUDY_KIT_PYTHON` 指向装了依赖的解释器，或让 `python` 在 PATH 中。
- 不联网；不上传任何文档。

## Limitations

- 只 OCR 每页最大图；一页多图可能漏内容。
- OCR 有错字/空格/大小写问题，公式/表格/结构图要回看原 PDF。
- 规则清洗不能保证 100% 去除个人信息；高风险资料仍需人工复核。
- 去重/回执尚未实现（P1）。

## Roadmap

- P1：去重（对比已有 Markdown 标题/关键词）、审批回执（源文件哈希 + 清洗报告哈希 + 批准人 + 链式记录）、测试。
- P2：DSH skill/CLI 打包、GitHub 发布、方法文章；只用合成数据。
- 指标：5 次有效对话，或 30–100 stars，或 1 个合作线索；无信号就保持内部工具。

## Data handling

- 全程本地处理；demo 使用合成数据。
- 清洗阶段移除无价值页和敏感信息；高风险资料仍需人工复核。
