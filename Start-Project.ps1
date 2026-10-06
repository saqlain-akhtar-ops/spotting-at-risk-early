$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$virtualPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (Test-Path -LiteralPath $virtualPython) {
    & $virtualPython run.py
} elseif (Test-Path -LiteralPath $bundledPython) {
    & $bundledPython run.py
} else {
    python run.py
}
