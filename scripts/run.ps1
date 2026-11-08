param(
    [Parameter(Mandatory = $true)][string]$Pdf,
    [Parameter(Mandatory = $true)][string]$Out,
    [int]$MaxPages = 0,
    [string]$DropPages = ""
)
$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Study Kit currently requires Windows (Windows.Media.Ocr).' }
$Py = $env:STUDY_KIT_PYTHON
if (-not $Py) { $Py = 'python' }
if (-not (Get-Command $Py -ErrorAction SilentlyContinue) -and -not (Test-Path -LiteralPath $Py)) {
    throw "python not found: $Py (set STUDY_KIT_PYTHON or install requirements)"
}
if (-not (Test-Path -LiteralPath $Pdf)) { throw "pdf not found: $Pdf" }

$pyArgs = @('-X', 'utf8', (Join-Path $PSScriptRoot 'extract_images.py'), '--pdf', $Pdf, '--out', $Out)
if ($MaxPages -gt 0) { $pyArgs += @('--max-pages', $MaxPages) }
& $Py @pyArgs
if ($LASTEXITCODE -ne 0) { throw "extract_images.py failed: $LASTEXITCODE" }

& (Join-Path $PSScriptRoot 'ocr_batch.ps1') -Dir (Join-Path $Out 'images')
if (-not $?) { throw "ocr_batch.ps1 failed" }

& $Py -X utf8 (Join-Path $PSScriptRoot 'assemble.py') --dir $Out
if ($LASTEXITCODE -ne 0) { throw "assemble.py failed: $LASTEXITCODE" }

$sanArgs = @('-X', 'utf8', (Join-Path $PSScriptRoot 'sanitize.py'), '--dir', $Out)
if ($DropPages) { $sanArgs += @('--drop-pages', $DropPages) }
& $Py -X utf8 (Join-Path $PSScriptRoot 'sanitize.py') --dir $Out --drop-pages $DropPages
if ($LASTEXITCODE -ne 0) { throw "sanitize.py failed: $LASTEXITCODE" }
if (-not (Test-Path -LiteralPath (Join-Path $Out 'extracted.sanitized.md'))) {
    throw 'sanitized output missing; check the pipeline logs'
}

Write-Output ("done: " + (Join-Path $Out 'extracted.sanitized.md'))
