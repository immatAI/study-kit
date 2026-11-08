param(
    [string]$Python = $env:STUDY_KIT_PYTHON
)
$ErrorActionPreference = 'Stop'
if (-not $Python) { $Python = 'python' }
Set-Location $PSScriptRoot\..
$out = 'demo\out-smoke'
if (Test-Path $out) { Remove-Item -LiteralPath $out -Recurse -Force }

Write-Output '== 1. pipeline =='
& powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run.ps1 -Pdf demo\slides.pdf -Out $out -DropPages 1
if ($LASTEXITCODE -ne 0) { throw 'pipeline failed' }
$sanitized = Join-Path $out 'extracted.sanitized.md'
if (-not (Test-Path $sanitized)) { throw 'missing sanitized output' }
if (Select-String -Path $sanitized -Pattern '^## Page 1$' -Quiet) { throw 'page 1 was not dropped' }
if (-not (Select-String -Path $sanitized -Pattern '^## Page 2$' -Quiet)) { throw 'page 2 missing' }

Write-Output '== 2. approve =='
& $Python scripts\receipt.py approve --dir $out --by tester
if ($LASTEXITCODE -ne 0) { throw 'approve failed' }

Write-Output '== 3. verify =='
& $Python scripts\receipt.py verify --dir $out
if ($LASTEXITCODE -ne 0) { throw 'verify failed' }

Write-Output '== 4. tamper detection =='
$backup = "$sanitized.bak"
Copy-Item $sanitized $backup -Force
Add-Content -LiteralPath $sanitized -Value "tampered" -Encoding UTF8
& $Python scripts\receipt.py verify --dir $out
$tamperExit = $LASTEXITCODE
Move-Item $backup $sanitized -Force
if ($tamperExit -eq 0) { throw 'tamper was not detected' }

Write-Output '== 5. dedupe =='
& $Python scripts\dedupe.py --draft $sanitized --existing demo\existing --json
if ($LASTEXITCODE -ne 0) { throw 'dedupe failed' }

Write-Output 'SMOKE PASS'
