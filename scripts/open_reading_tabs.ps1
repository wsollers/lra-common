param(
    [ValidateSet("analysis", "metric-spaces", "algebra", "number-systems", "topology", "all")]
    [string]$Track = "analysis",

    [switch]$List,
    [switch]$NoNewProfile
)

$ErrorActionPreference = "Stop"

$readingRoot = "D:\Readings\Analysis"

$tracks = @{
    "analysis" = @(
        "Analysis 1 - Tao.pdf",
        "Mathematical Analysis Volume 1 - Zorich.pdf",
        "Introduction to Real Analysis 3rd by Robert G. Bartle.pdf",
        "Basic Analysis I - Lebl.pdf",
        "Elementary Real Analysis - Bruckner.pdf",
        "Sequences and Series Theory and Practice - de Sa.pdf",
        "Real Mathematical Analysis - Pugh.pdf",
        "Real Analysis for the Undergraduate-Pons.pdf",
        "Real Analysis Foundations and Functions of One Variable - Laczkovich.pdf",
        "Introduction to Mathematical Analysis - Deo.pdf",
        "Basic Real Analysis - Sohrab.pdf",
        "Real Analysis and Applications - Davidson.pdf",
        "UnderstandingAnalysis-Abbott.pdf",
        "Principles_of_Mathematical_Analysis-Rudin.pdf"
    )

    "metric-spaces" = @(
        "Metric Spaces\An_Introduction_to_Metric_Spaces.pdf",
        "Metric Spaces\Metric Spaces - Copson.pdf",
        "Metric Spaces\Metric Spaces - Vasudeva.pdf",
        "Metric Spaces\A Comprehensive Textbook on Metric Spaces - Kainth.pdf",
        "metric-spaces.pdf",
        "metric-spaces (1).pdf",
        "calculus\(Springer Undergraduate Mathematics Series) Robert Magnus - Metric Spaces - A Companion to Analysis-Springer Nature Switzerland (2022).pdf"
    )

    "algebra" = @(
        "calculus\Algebra e2 - Aluffi.pdf",
        "A First Course in Group Theory - Davvaz.pdf",
        "A Gentle Introduction to Group Theory - Subaiei.pdf",
        "Introduction to Linear and Matrix Algebra - Johnston.pdf",
        "Introduction to Linear and Matrix Algebra.pdf",
        "New folder\U ndergradua te Algebra e1 - Lang.pdf",
        "New folder\Galois Theory Through - Through.pdf",
        "A Course in Combinatorics e2 - Lint.pdf",
        "Introduction to Combinatorics and Graph Theory.pdf"
    )

    "number-systems" = @(
        "The Real Numbers - Stillwell.pdf",
        "The real numbers and completeness.pdf",
        "An Axiomatic Construction of the Real Number System.pdf",
        "Foundations of Analysis - Landau.pdf",
        "number-systems-and-the-foundations-of-analysis-mendelson.pdf",
        "The number systems Foundations of algebra and analysis - Feferman.pdf",
        "Numbers - Ebbinghaus.pdf",
        "New folder\The Number Systems of Analysis - rational sequences.pdf",
        "Transcendental Number - M. Ram Murty.pdf"
    )

    "topology" = @(
        "calculus\topology.pdf",
        "Topological Spaces - From Distance to Neighborhood - Buskes.pdf",
        "New folder\Arnoud van Rooij From Distance to Neighborhood e2 - Buskes.pdf",
        "Metric Spaces\An_Introduction_to_Metric_Spaces.pdf",
        "Metric Spaces\Metric Spaces - Copson.pdf",
        "New folder\and Riemann Surfaces for Undergraduates - Curves.pdf",
        "calculus\FOAGsep1815public.pdf"
    )
}

function Find-Chrome {
    $candidates = @(
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "$env:LocalAppData\Google\Chrome\Application\chrome.exe"
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            return $candidate
        }
    }

    $command = Get-Command chrome.exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    throw "Could not find chrome.exe."
}

function Convert-ToFileUrl([string]$Path) {
    $resolved = Resolve-Path -LiteralPath $Path
    return ([System.Uri]$resolved.ProviderPath).AbsoluteUri
}

function Get-TrackFiles([string]$Name) {
    $files = @()
    foreach ($relativePath in $tracks[$Name]) {
        $fullPath = Join-Path $readingRoot $relativePath
        if (Test-Path -LiteralPath $fullPath) {
            $files += [pscustomobject]@{
                Track = $Name
                RelativePath = $relativePath
                FullPath = $fullPath
                Exists = $true
            }
        } else {
            $files += [pscustomobject]@{
                Track = $Name
                RelativePath = $relativePath
                FullPath = $fullPath
                Exists = $false
            }
        }
    }
    return $files
}

function Open-Track([string]$Name) {
    $chrome = Find-Chrome
    $files = @(Get-TrackFiles $Name)
    $missing = @($files | Where-Object { -not $_.Exists })
    $existing = @($files | Where-Object { $_.Exists })

    if ($missing.Count -gt 0) {
        Write-Warning "Missing $($missing.Count) file(s) for track '$Name':"
        $missing | ForEach-Object { Write-Warning "  $($_.RelativePath)" }
    }

    if ($existing.Count -eq 0) {
        throw "No existing PDF files found for track '$Name'."
    }

    $args = @("--new-window")
    if (-not $NoNewProfile) {
        $profileDir = Join-Path $env:TEMP "lra-reading-chrome-$Name"
        New-Item -ItemType Directory -Force -Path $profileDir | Out-Null
        $args += "--user-data-dir=$profileDir"
    }
    $args += ($existing | ForEach-Object { Convert-ToFileUrl $_.FullPath })

    Write-Host "Opening $($existing.Count) PDF tab(s) for '$Name'."
    Start-Process -FilePath $chrome -ArgumentList $args
}

if ($List) {
    $names = if ($Track -eq "all") { $tracks.Keys | Sort-Object } else { @($Track) }
    foreach ($name in $names) {
        Write-Host ""
        Write-Host "[$name]"
        Get-TrackFiles $name | ForEach-Object {
            $mark = if ($_.Exists) { "OK " } else { "MISS" }
            Write-Host ("  {0}  {1}" -f $mark, $_.RelativePath)
        }
    }
    exit 0
}

if ($Track -eq "all") {
    foreach ($name in ($tracks.Keys | Sort-Object)) {
        Open-Track $name
    }
} else {
    Open-Track $Track
}
