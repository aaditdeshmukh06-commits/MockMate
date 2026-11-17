<#
.SYNOPSIS
    Builds the MockMate Lambda deployment package (lambda.zip)

.DESCRIPTION
    Creates a deployment package for AWS Lambda (Python 3.12, x86_64 Linux).
    - Installs dependencies from ai/requirements.txt (excluding boto3/botocore)
    - Copies handler and shared modules to package folder (excluding __pycache__, local_test.py, .env)
    - Runs import checker against ai/package
    - Zips CONTENTS of package folder (not the folder itself) to lambda.zip at repo root using shutil.make_archive
    - Prints zip size, .py files at zip root, and handler mapping table

.NOTES
    Run from repository root: .\scripts\build_lambda.ps1
    Requires: Python 3.12+, pip, AWS CLI (for deployment)
#>

param(
    [switch]$Force = $false
)

# Configuration
$RepoRoot = Split-Path -Parent $PSScriptRoot
$AiDir = Join-Path $RepoRoot "ai"
$PackageDir = Join-Path $AiDir "package"
$RequirementsFile = Join-Path $AiDir "requirements.txt"
$ZipPath = Join-Path $RepoRoot "lambda.zip"
$PythonVersion = "3.12"
$Platform = "manylinux2014_x86_64"
$MaxZipSizeMB = 50

# Handler mapping for output table
$Handlers = @(
    @{ Function = "mockmate-start";       Handler = "start_interview.lambda_handler" },
    @{ Function = "mockmate-answer";      Handler = "submit_answer.lambda_handler" },
    @{ Function = "mockmate-report";      Handler = "get_report.lambda_handler" },
    @{ Function = "mockmate-history";     Handler = "list_interviews.lambda_handler" },
    @{ Function = "mockmate-save";        Handler = "save_report.lambda_handler" }
)

# Colors for output
$Green = [ConsoleColor]::Green
$Yellow = [ConsoleColor]::Yellow
$Red = [ConsoleColor]::Red
$Cyan = [ConsoleColor]::Cyan
$Gray = [ConsoleColor]::Gray

function Write-Status($msg) { Write-Host "  $msg" -ForegroundColor $Cyan }
function Write-Success($msg) { Write-Host "  [OK] $msg" -ForegroundColor $Green }
function Write-Warning($msg) { Write-Host "  [WARN] $msg" -ForegroundColor $Yellow }
function Write-Error($msg) { Write-Host "  [ERROR] $msg" -ForegroundColor $Red }

Write-Host "`n============================================" -ForegroundColor $Cyan
Write-Host "MockMate Lambda Build Script" -ForegroundColor $Cyan
Write-Host "============================================`n" -ForegroundColor $Cyan

# Check prerequisites
Write-Status "Checking prerequisites..."

if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found in PATH"
    exit 1
}
$PythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }
$PythonVer = & $PythonCmd --version 2>&1
Write-Success "Python: $PythonVer"

if (-not (Get-Command pip -ErrorAction SilentlyContinue) -and -not (Get-Command pip3 -ErrorAction SilentlyContinue)) {
    Write-Error "pip not found in PATH"
    exit 1
}
$PipCmd = if (Get-Command pip -ErrorAction SilentlyContinue) { "pip" } else { "pip3" }
Write-Success "pip: $($PipCmd)"

if (-not (Test-Path $RequirementsFile)) {
    Write-Error "Requirements file not found: $RequirementsFile"
    exit 1
}
Write-Success "Requirements: $RequirementsFile"

# Clean old build
Write-Host "`n[1/6] Cleaning old build artifacts..." -ForegroundColor $Cyan
if (Test-Path $PackageDir) {
    Remove-Item -Recurse -Force $PackageDir -ErrorAction SilentlyContinue
    Write-Success "Removed $PackageDir"
}
if (Test-Path $ZipPath) {
    Remove-Item -Force $ZipPath -ErrorAction SilentlyContinue
    Write-Success "Removed $ZipPath"
}
New-Item -ItemType Directory -Path $PackageDir | Out-Null
Write-Success "Created $PackageDir"

# Create filtered requirements (exclude boto3, botocore)
Write-Host "`n[2/6] Preparing filtered requirements..." -ForegroundColor $Cyan
$FilteredReqs = Join-Path $AiDir "requirements.lambda.txt"
$Content = Get-Content $RequirementsFile -Raw
$FilteredLines = $Content -split "`n" | Where-Object {
    $_ -notmatch '^\s*(boto3|botocore)(\s|$|==|>=|<=|~=|!=)' -and $_ -notmatch '^\s*#' -and $_ -notmatch '^\s*$'
}
$Filtered = $FilteredLines -join "`n"
Set-Content -Path $FilteredReqs -Value $Filtered -Encoding UTF8
Write-Success "Filtered requirements written to $FilteredReqs"
Write-Host "  Contents:`n$Filtered" -ForegroundColor $Gray

# Install dependencies
Write-Host "`n[3/6] Installing dependencies for $Platform (Python $PythonVersion)..." -ForegroundColor $Cyan
$InstallArgs = @(
    "install",
    "-r", $FilteredReqs,
    "-t", $PackageDir,
    "--platform", $Platform,
    "--python-version", $PythonVersion,
    "--only-binary=:all:",
    "--implementation", "cp",
    "--no-cache-dir",
    "--quiet"
)
Write-Status "Running: $PipCmd $($InstallArgs -join ' ')"
$InstallResult = & $PipCmd @InstallArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "pip install failed with exit code $LASTEXITCODE"
    Write-Host $InstallResult -ForegroundColor $Red
    exit 1
}
Write-Success "Dependencies installed to $PackageDir"

# Copy runtime Python files (exclude __pycache__, local_test.py, .env)
Write-Host "`n[4/6] Copying handler and shared modules..." -ForegroundColor $Cyan

$FilesToCopy = @(
    "handlers/start_interview.py"
    "handlers/submit_answer.py"
    "handlers/get_report.py"
    "handlers/list_interviews.py"
    "handlers/save_report.py"
    "handlers/__init__.py"
    "shared/__init__.py"
    "shared/database.py"
    "shared/evaluation.py"
    "shared/questions.py"
    "shared/reporting.py"
    "shared/utils.py"
    "shared/db_utils.py"
)

$CopiedCount = 0
foreach ($relPath in $FilesToCopy) {
    $src = Join-Path $AiDir $relPath
    $dest = Join-Path $PackageDir $relPath
    $destDir = Split-Path $dest
    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }
    if (Test-Path $src) {
        Copy-Item $src $dest -Force
        $CopiedCount++
        Write-Success "Copied $relPath"
    } else {
        Write-Warning "Source not found: $relPath"
    }
}
Write-Host "  Copied $CopiedCount files" -ForegroundColor $Gray

# Run import checker
Write-Host "`n[5/6] Running import checker..." -ForegroundColor $Cyan
$CheckImportsScript = Join-Path $RepoRoot "scripts/check_imports.py"
if (Test-Path $CheckImportsScript) {
    $CheckResult = & $PythonCmd $CheckImportsScript 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Import checker failed"
        Write-Host $CheckResult -ForegroundColor $Red
        exit 1
    }
    Write-Host $CheckResult -ForegroundColor $Gray
    Write-Success "Import check passed"
} else {
    Write-Warning "Import checker script not found at $CheckImportsScript"
}

# Create zip file using Python (exclude __pycache__)
Write-Host "`n[6/6] Creating lambda.zip..." -ForegroundColor $Cyan

$ZipScript = @"
import zipfile, os, sys
zip_path = r'$ZipPath'
package_dir = r'$PackageDir'

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(package_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for f in files:
            if not f.endswith('.pyc') and not f.endswith('.pyo'):
                fp = os.path.join(root, f)
                # Archive path relative to package_dir (so contents are at zip root)
                arc = os.path.relpath(fp, package_dir)
                zf.write(fp, arc)
print(f'Created {zip_path}')
"@

$ZipScriptPath = Join-Path $env:TEMP "build_lambda_zip.py"
Set-Content -Path $ZipScriptPath -Value $ZipScript -Encoding UTF8
$ZipResult = & $PythonCmd $ZipScriptPath 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python zip creation failed"
    Write-Host $ZipResult -ForegroundColor $Red
    Remove-Item $ZipScriptPath -ErrorAction SilentlyContinue
    exit 1
}
Write-Host $ZipResult -ForegroundColor $Gray
Remove-Item $ZipScriptPath -ErrorAction SilentlyContinue
Write-Success "Created $ZipPath"

# Verify zip contents
Write-Host "`n============================================" -ForegroundColor $Cyan
Write-Host "Verification" -ForegroundColor $Cyan
Write-Host "============================================`n" -ForegroundColor $Cyan

# List zip contents
Write-Status "Zip contents (top-level):"
$ListScript = @"
import zipfile
with zipfile.ZipFile(r'$ZipPath', 'r') as zf:
    for name in sorted(zf.namelist()):
        info = zf.getinfo(name)
        print(f'  {info.file_size:>8} bytes  {name}')
"@
$ListScriptPath = Join-Path $env:TEMP "build_lambda_list.py"
Set-Content -Path $ListScriptPath -Value $ListScript -Encoding UTF8
& $PythonCmd $ListScriptPath 2>&1
Remove-Item $ListScriptPath -ErrorAction SilentlyContinue

# Print .py files at zip root
Write-Host "`nPython files at zip root:"
$RootFilesScript = @"
import zipfile
with zipfile.ZipFile(r'$ZipPath', 'r') as zf:
    for name in sorted(zf.namelist()):
        if name.endswith('.py') and '/' not in name and '\\' not in name:
            info = zf.getinfo(name)
            print(f'  {info.file_size:>8} bytes  {name}')
"@
$RootFilesScriptPath = Join-Path $env:TEMP "build_lambda_rootfiles.py"
Set-Content -Path $RootFilesScriptPath -Value $RootFilesScript -Encoding UTF8
& $PythonCmd $RootFilesScriptPath 2>&1
Remove-Item $RootFilesScriptPath -ErrorAction SilentlyContinue

# Check for boto3/botocore in package
Write-Host "`nChecking for excluded packages..."
$CheckScript = @"
import zipfile
found = False
with zipfile.ZipFile(r'$ZipPath', 'r') as zf:
    for name in zf.namelist():
        if name.startswith('boto3/') or name.startswith('botocore/'):
            print(f'FOUND: {name}')
            found = True
            break
    if not found:
        print('OK')
"@
$CheckScriptPath = Join-Path $env:TEMP "build_lambda_check.py"
Set-Content -Path $CheckScriptPath -Value $CheckScript -Encoding UTF8
$HasBoto3 = & $PythonCmd $CheckScriptPath 2>&1
Remove-Item $CheckScriptPath -ErrorAction SilentlyContinue
if ($HasBoto3 -ne "OK") {
    Write-Warning "Found boto3/botocore in package (should be excluded)"
    Write-Host $HasBoto3 -ForegroundColor $Yellow
} else {
    Write-Success "No boto3/botocore in package (correctly excluded)"
}

# Check zip size
$ZipSizeBytes = (Get-Item $ZipPath).Length
$ZipSizeMB = [math]::Round($ZipSizeBytes / 1MB, 2)
Write-Host "`nZip size: $ZipSizeMB MB" -ForegroundColor $Cyan
if ($ZipSizeMB -gt $MaxZipSizeMB) {
    Write-Warning "Zip size exceeds ${MaxZipSizeMB}MB limit for Lambda direct upload!"
    Write-Warning "Consider using S3 for deployment or reducing dependencies."
} else {
    Write-Success "Zip size is within Lambda direct upload limit (${MaxZipSizeMB}MB)"
}

# Print handler table
Write-Host "`n============================================" -ForegroundColor $Cyan
Write-Host "Lambda Function Handlers" -ForegroundColor $Cyan
Write-Host "============================================`n" -ForegroundColor $Cyan
Write-Host "Function Name".PadRight(25) + "Handler" -ForegroundColor $Gray
Write-Host ("-" * 60) -ForegroundColor $Gray
foreach ($h in $Handlers) {
    Write-Host $h.Function.PadRight(25) + $h.Handler
}
Write-Host ""

# Final summary
Write-Host "`n============================================" -ForegroundColor $Cyan
Write-Host "Build Complete!" -ForegroundColor $Green
Write-Host "============================================`n" -ForegroundColor $Cyan
Write-Host "Output: $ZipPath" -ForegroundColor $Cyan
Write-Host "Size:   $ZipSizeMB MB" -ForegroundColor $Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor $Yellow
Write-Host "  1. Deploy with: aws lambda update-function-code --function-name mockmate-start --zip-file fileb://lambda.zip" -ForegroundColor $Gray
Write-Host "  2. Repeat for mockmate-answer, mockmate-report, mockmate-history, mockmate-save" -ForegroundColor $Gray
Write-Host "  3. Set environment variables: USE_MOCK, TABLE_NAME, REGION, GROQ_API_KEY" -ForegroundColor $Gray
Write-Host ""