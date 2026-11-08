---
name: study-kit
description: 本地把图片型 PDF 变成“已清洗、可核对”的 Markdown：Windows OCR、无价值页/敏感信息清洗、去重、审批回执。内容无关，可用合成数据演示。
whenToUse: 需要把扫描/截图型 PDF 转成可检索笔记，又不希望上传文档或把无价值页/敏感信息带进知识库时；或需要在写入前留审批回执时。
---

# Study Kit

本 skill 是对仓库根 `study-kit.ps1` 的入口说明；脚本都在 `scripts/`，demo 在 `demo/`。

## 前置

- Windows 10/11（OCR 依赖 `Windows.Media.Ocr`）。
- Python 3.11+，`pip install -r requirements.txt`。
- 设置 `STUDY_KIT_PYTHON` 指向该解释器，或让 `python` 在 PATH。

## 用法

```powershell
# 1) 跑流水线：抽图 + OCR + 清洗
.\study-kit.ps1 run -Pdf <input.pdf> -Out <outdir> -DropPages 1-3

# 2) 审批回执
.\study-kit.ps1 approve --dir <outdir> --by reviewer

# 3) 校验回执/篡改
.\study-kit.ps1 verify --dir <outdir>

# 4) 与已有 Markdown 做廉价去重
.\study-kit.ps1 dedupe --draft <outdir>\extracted.sanitized.md --existing <notes-dir>
```

## 输出

- `extracted.sanitized.md`：清洗后 Markdown；
- `sanitize-report.json`：丢弃页/脱敏项；
- `receipt.approved.json` + `receipts.jsonl`：源文件/清洗报告/输出哈希，链式回执。

## 边界

- 只 OCR 每页最大图；一页多图可能漏。
- 规则清洗不能保证 100% 去个人信息；高风险资料要人工复核。
- OCR 有错字，公式/表格/结构图回看原 PDF。
- 不联网；不要把敏感资料推到公开仓库。
