param(
    [string]$Root = "C:\\Users\\Tuan Tu Tran\\Documents\\code\\CommunicationSystem\\Tran\\AppData\\Local\\Temp"
)
Write-Host "Cleaning Conda temp folders under: $Root"
if (-Not (Test-Path $Root)) {
    Write-Host "Path not found: $Root" -ForegroundColor Yellow
    exit 0
}
$items = Get-ChildItem -Path $Root -Directory -Filter "conda-*" -ErrorAction SilentlyContinue
if ($items.Count -eq 0) {
    Write-Host "No conda-* folders found." -ForegroundColor Green
    exit 0
}
# Ensure no conda process is running
$condaProc = Get-Process -Name conda -ErrorAction SilentlyContinue
if ($condaProc) {
    Write-Host "Conda process detected. Please close Conda operations before cleanup." -ForegroundColor Red
    exit 1
}
$items | ForEach-Object {
    Write-Host "Removing: $($_.FullName)"
    Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction Continue
}
Write-Host "Cleanup complete." -ForegroundColor Green
