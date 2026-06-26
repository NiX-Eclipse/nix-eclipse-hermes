[CmdletBinding()]
param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ForwardArgs
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3 (Join-Path $Root "scripts/build.py") --repo-root $Root @ForwardArgs
  exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
  & python (Join-Path $Root "scripts/build.py") --repo-root $Root @ForwardArgs
  exit $LASTEXITCODE
}

throw "Python not found on PATH."