$ErrorActionPreference = 'Stop'
$scriptFile = Join-Path $PSScriptRoot 'remote_ai.py'
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $scriptFile @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $scriptFile @args
} else {
    Write-Error 'Install Python 3.10 or newer from https://www.python.org/downloads/'
    exit 1
}
exit $LASTEXITCODE
