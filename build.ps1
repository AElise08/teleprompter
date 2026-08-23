Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$cmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $cmd) {
    $cmd = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $cmd) {
    Write-Error "Python nao encontrado. Instale em https://www.python.org/downloads/ e marque 'tcl/tk'."
}

$argv = @("teleprompter.py") + @($args)
& $cmd.Source @argv
