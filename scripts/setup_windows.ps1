<#
.SYNOPSIS
    One-click native Windows PowerShell setup script for Legal Saathi AI Consumer Lawyer.

.DESCRIPTION
    Automates prerequisite verification (git, uv), virtual environment synchronization,
    environment configuration (.env initialization from .env.example), statutory corpus
    ingestion, and quality gate validation via pytest on native Windows 11 / 10.

.PARAMETER SkipIngestion
    Skips the statutory corpus ingestion step (scripts/ingest_corpus.py).

.PARAMETER SkipTests
    Skips the automated quality gate test validation step (pytest).

.PARAMETER RebuildIndex
    Forces a clean rebuild of the persistent vector and BM25 index.

.PARAMETER Dev
    Syncs optional development dependencies (ruff, mypy, ty, pytest). Default: $true.

.EXAMPLE
    .\scripts\setup_windows.ps1

.EXAMPLE
    .\scripts\setup_windows.ps1 -RebuildIndex -Dev
#>

[CmdletBinding()]
param(
    [switch]$SkipIngestion,
    [switch]$SkipTests,
    [switch]$RebuildIndex,
    [switch]$Dev = $true
)

# ------------------------------------------------------------------------------
# 1. Environment & Console UTF-8 Initialization
# ------------------------------------------------------------------------------
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Enforce UTF-8 encoding for Windows PowerShell / PowerShell Core
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"

# Resolve repository root by locating pyproject.toml
$CurrentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
while ($CurrentDir -and -not (Test-Path (Join-Path $CurrentDir "pyproject.toml"))) {
    $ParentDir = Split-Path -Parent $CurrentDir
    if ($ParentDir -eq $CurrentDir) { break }
    $CurrentDir = $ParentDir
}
if (Test-Path (Join-Path $CurrentDir "pyproject.toml")) {
    $RepoRoot = (Resolve-Path $CurrentDir).Path
} else {
    $RepoRoot = (Resolve-Path (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..")).Path
}
Set-Location -Path $RepoRoot

# ------------------------------------------------------------------------------
# Output Formatting Helpers
# ------------------------------------------------------------------------------
function Write-StepBanner {
    param([int]$StepNumber, [string]$Title)
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host " [Step $StepNumber/5] $Title" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host " [OK] $Message" -ForegroundColor Green
}

function Write-WarningMessage {
    param([string]$Message)
    Write-Host " [WARNING] $Message" -ForegroundColor Yellow
}

function Write-FailureAndExit {
    param([string]$Message)
    Write-Host ""
    Write-Host " [ERROR] $Message" -ForegroundColor Red
    Write-Host ("=" * 80) -ForegroundColor Red
    exit 1
}

# ------------------------------------------------------------------------------
# Banner Header
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host ("=" * 80) -ForegroundColor Blue
Write-Host "         LEGAL SAATHI: ONE-CLICK NATIVE WINDOWS SETUP" -ForegroundColor White
Write-Host "     AI Consumer Lawyer for India (CPA 2019 & E-Commerce Rules 2020)" -ForegroundColor Gray
Write-Host " Repository Root: $RepoRoot" -ForegroundColor DarkGray
Write-Host ("=" * 80) -ForegroundColor Blue

# ------------------------------------------------------------------------------
# STEP 1: Verify Toolchain Prerequisites (git & uv)
# ------------------------------------------------------------------------------
Write-StepBanner 1 "Verifying Toolchain Prerequisites (git & uv)"

# 1.1 Check git
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-FailureAndExit @"
Git was not found in your system PATH.
Please install Git for Windows:
  winget install --id Git.Git -e --source winget
or download from https://git-scm.com/download/win
"@
}
$gitVersion = (& git --version)
Write-Success "Git detected: $gitVersion"

# 1.2 Check uv
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uvCmd) {
    Write-FailureAndExit @"
Astral 'uv' package manager was not found in your system PATH.
To install uv natively on Windows, run:
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
or via Windows Package Manager:
  winget install --id astral-sh.uv -e --source winget
"@
}
$uvVersion = (& uv --version)
Write-Success "uv package manager detected: $uvVersion"

# ------------------------------------------------------------------------------
# STEP 2: Configure Environment (.env)
# ------------------------------------------------------------------------------
Write-StepBanner 2 "Checking Environment Configuration (.env)"

$EnvPath = Join-Path $RepoRoot ".env"
$EnvExamplePath = Join-Path $RepoRoot ".env.example"

if (-not (Test-Path $EnvPath)) {
    if (Test-Path $EnvExamplePath) {
        Copy-Item -Path $EnvExamplePath -Destination $EnvPath -Force
        Write-Success "Created '.env' from template '.env.example'."
        Write-WarningMessage "Remember to configure your API keys (GROQ_API_KEY, etc.) in '.env' for live evaluation."
    } else {
        Write-WarningMessage "'.env.example' not found; continuing with runtime environment variables."
    }
} else {
    Write-Success "Found existing '.env' file; preserving current configuration."
}

# ------------------------------------------------------------------------------
# STEP 3: Initialize Virtual Environment & Sync Dependencies (uv sync)
# ------------------------------------------------------------------------------
Write-StepBanner 3 "Synchronizing Virtual Environment & Dependencies"

Write-Host "Running uv sync to resolve and install Python virtual environment..." -ForegroundColor Gray
if ($Dev) {
    & uv sync --extra dev
} else {
    & uv sync
}

if ($LASTEXITCODE -ne 0) {
    Write-FailureAndExit "uv sync failed with exit code $LASTEXITCODE. Please verify internet connectivity and pyproject.toml."
}
Write-Success "Virtual environment (.venv) synchronized successfully."

# ------------------------------------------------------------------------------
# STEP 4: Ingest Statutory Corpus
# ------------------------------------------------------------------------------
Write-StepBanner 4 "Ingesting Indian Consumer Law Corpus"

if ($SkipIngestion) {
    Write-WarningMessage "Statutory corpus ingestion skipped (-SkipIngestion specified)."
} else {
    $IngestScript = Join-Path $RepoRoot "scripts\ingest_corpus.py"
    if (-not (Test-Path $IngestScript)) {
        Write-FailureAndExit "Corpus ingestion script not found at $IngestScript"
    }

    $IngestArgs = @(
        "run",
        "python",
        $IngestScript,
        "--corpus-dir",
        "data/statutes",
        "--persist-dir",
        "data/index/chroma",
        "--validate"
    )
    if ($RebuildIndex) {
        $IngestArgs += "--rebuild"
    }

    Write-Host "Executing statutory ingestion via: uv $($IngestArgs -join ' ')..." -ForegroundColor Gray
    & uv $IngestArgs

    if ($LASTEXITCODE -ne 0) {
        Write-FailureAndExit "Corpus ingestion failed with exit code $LASTEXITCODE."
    }
    Write-Success "Statutory corpus chunked and indexed into hybrid BM25 + vector store."
}

# ------------------------------------------------------------------------------
# STEP 5: Validate Quality Gates (Automated Test Suite)
# ------------------------------------------------------------------------------
Write-StepBanner 5 "Validating Quality Gates (pytest)"

if ($SkipTests) {
    Write-WarningMessage "Automated quality gate testing skipped (-SkipTests specified)."
} else {
    Write-Host "Running pytest across all unit and integration suites..." -ForegroundColor Gray
    & uv run pytest -q

    if ($LASTEXITCODE -ne 0) {
        Write-FailureAndExit "Quality gates failed! Please inspect test failure outputs above."
    }
    Write-Success "All unit and integration test suites passed cleanly."
}

# ------------------------------------------------------------------------------
# Summary & Launch Instructions
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host ("=" * 80) -ForegroundColor Green
Write-Host "       [SUCCESS] LEGAL SAATHI ENVIRONMENT READY FOR EVALUATION" -ForegroundColor White
Write-Host ("=" * 80) -ForegroundColor Green
Write-Host ""
Write-Host " Quick Launch Options:" -ForegroundColor White
Write-Host "   1. Launch Interactive Gradio UI:" -ForegroundColor Yellow
Write-Host "      uv run python -m legal_assistant.ui.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "   2. Run Live Evaluation Benchmark Scenarios (5 disputes):" -ForegroundColor Yellow
Write-Host "      uv run python scripts/generate_raw_outputs.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "   3. Re-run Quality Gates & Linters:" -ForegroundColor Yellow
Write-Host "      uv run ruff check ." -ForegroundColor DarkGray
Write-Host "      uv run ty check" -ForegroundColor DarkGray
