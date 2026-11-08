param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('run', 'approve', 'verify', 'dedupe')]
    [string]$Command,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)
$ErrorActionPreference = 'Stop'
$Python = $env:STUDY_KIT_PYTHON
if (-not $Python) { $Python = 'python' }
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

switch ($Command) {
    'run'     { & (Join-Path $Root 'scripts\run.ps1') @Rest }
    'approve' { & $Python (Join-Path $Root 'scripts\receipt.py') approve @Rest }
    'verify'  { & $Python (Join-Path $Root 'scripts\receipt.py') verify @Rest }
    'dedupe'  { & $Python (Join-Path $Root 'scripts\dedupe.py') @Rest }
}
exit $LASTEXITCODE
