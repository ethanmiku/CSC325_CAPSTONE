# Windows setup: downloads Godot, sets up the Python virtual environment, and
# sets up backend/.env for local development. macOS uses install-prereqs.sh.
#
# Usage: powershell -ExecutionPolicy Bypass -File .\install-prereqs.ps1
#
# Windows blocks .ps1 scripts by default (execution policy). The -ExecutionPolicy
# Bypass flag above only applies to this one run and changes no system settings.
# Alternatives:
#   - Allow local scripts for your user once:
#       Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#   - If you downloaded the repo as a zip, unblock this file:
#       Unblock-File .\install-prereqs.ps1

$ErrorActionPreference = 'Stop'

$EnvExample = Join-Path $PSScriptRoot 'backend/.env.example'
$EnvFile = Join-Path $PSScriptRoot 'backend/.env'
$Requirements = Join-Path $PSScriptRoot 'backend/requirements.txt'
$VenvDir = Join-Path $PSScriptRoot '.venv'

$GodotUrl = 'https://downloads.godotengine.org/?version=4.7.2&flavor=stable&slug=win64.exe.zip&platform=windows.64'

# Characters Django uses for its generated secret keys.
$SecretKeyChars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

# Edit these to change what each step shows.
$GodotTitle = 'Step 1: Download Godot 4.7.2 for Windows'
$GodotPrompt = @'
Opens the Godot 4.7.2 Windows download in your browser.
Choose Skip if you already have Godot 4.7.2 installed.
'@

$VenvTitle = 'Step 2: Python virtual environment'
$VenvPrompt = @'
Creates .venv in the repository root with Python 3.14 and
installs the packages from backend/requirements.txt into it.
'@

$EnvTitle = 'Step 3: Set up backend/.env'
$EnvPrompt = @'
Copies backend/.env.example to backend/.env and can walk you
through filling in each value.
'@

function Show-Banner([string]$Title, [string]$Message) {
    Write-Host ''
    Write-Host '=================================================='
    Write-Host "  $Title"
    Write-Host '=================================================='
    Write-Host $Message
    Write-Host '=================================================='
}

# Shows a step's title and message, then asks to continue.
# Returns $true to run the step, $false to skip it.
function Show-Prompt([string]$Title, [string]$Message) {
    Show-Banner $Title $Message
    return Confirm-Continue 'Do you wish to continue?'
}

# Asks a y/N question. Returns $true for yes, $false for anything else.
function Confirm-Continue([string]$Question) {
    $answer = Read-Host "$Question [y/N]"
    return $answer -match '^(y|yes)$'
}

function Invoke-GodotStep {
    Show-Banner $GodotTitle $GodotPrompt
    Write-Host '  1) Download'
    Write-Host '  2) Skip'
    Write-Host '  3) Exit'
    while ($true) {
        $choice = Read-Host 'Enter 1, 2, or 3'
        if ($choice -eq '1') { Invoke-GodotDownload; return }
        if ($choice -eq '2') { Write-Host 'Skipping Godot download.'; return }
        if ($choice -eq '3') { Write-Host 'Exiting.'; exit 0 }
        Write-Host 'Invalid choice.'
    }
}

function Invoke-GodotDownload {
    Write-Host ''
    Write-Host 'Opening the Godot download in your browser:'
    Write-Host "  $GodotUrl"
    try {
        Start-Process $GodotUrl
    } catch {
        Write-Host 'Could not open a browser. Copy the link above into your browser instead.'
    }
    Write-Host 'When it finishes, extract the zip. Godot_v4.7.2-stable_win64.exe runs without installing.'
}

# Returns the first Python command that runs, as an array of the command and
# its arguments, or $null if none do.
function Find-Python {
    foreach ($candidate in @(@('py', '-3.14'), @('python'), @('python3'))) {
        $exe = $candidate[0]
        $pyArgs = @($candidate | Select-Object -Skip 1)
        try {
            & $exe @pyArgs --version | Out-Null
            if ($LASTEXITCODE -eq 0) { return , $candidate }
        } catch {
            continue
        }
    }
    return $null
}

function Initialize-Venv {
    Write-Host ''
    $python = Find-Python
    if (-not $python) {
        Write-Host 'Python 3.14 was not found. Install it (see backend/SETUP_WIN.md)'
        Write-Host 'and rerun this script.'
        return
    }
    $exe = $python[0]
    $pyArgs = @($python | Select-Object -Skip 1)

    $version = & $exe @pyArgs -c "import sys; print('%d.%d.%d' % sys.version_info[:3])"
    Write-Host "Using $($python -join ' ') (Python $version)."
    if ($version -notlike '3.14.*') {
        Write-Host "Warning: this project expects Python 3.14. Continuing with $version."
    }

    # Windows puts the activate script in Scripts\; macOS and Linux use bin/.
    $winActivate = Join-Path $VenvDir 'Scripts/Activate.ps1'
    $unixActivate = Join-Path $VenvDir 'bin/Activate.ps1'
    if ((Test-Path $winActivate) -or (Test-Path $unixActivate)) {
        Write-Host 'Reusing existing .venv.'
    } else {
        Write-Host 'Creating .venv...'
        & $exe @pyArgs -m venv $VenvDir
        if ($LASTEXITCODE -ne 0) {
            Write-Host 'Error: could not create .venv.'
            return
        }
    }

    if (Test-Path $winActivate) {
        . $winActivate
    } else {
        . $unixActivate
    }

    Write-Host ''
    Write-Host 'Installing packages from backend/requirements.txt...'
    python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Error: could not upgrade pip.'
        Write-Host 'Activate .venv and run: python -m pip install --upgrade pip'
        return
    }
    python -m pip install -r $Requirements
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Error: could not install the packages.'
        Write-Host 'Activate .venv and run: python -m pip install -r backend/requirements.txt'
        return
    }
    python -m pip check
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'Error: pip check found dependency problems.'
        return
    }
    Write-Host 'Packages installed.'
}

# Returns a random 50-character Django secret key.
function New-SecretKey {
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $byte = New-Object byte[] 1
    $key = ''
    while ($key.Length -lt 50) {
        $rng.GetBytes($byte)
        # 250 is the largest multiple of 50 that fits in a byte, so skipping
        # higher values keeps every character equally likely.
        if ($byte[0] -lt 250) { $key += $SecretKeyChars[$byte[0] % $SecretKeyChars.Length] }
    }
    return $key
}

# Returns each KEY from an env file, skipping blank lines and comments.
function Get-EnvKeys([string]$Path) {
    foreach ($line in Get-Content $Path) {
        if ($line -match '^([A-Za-z_][^=]*)=') { $Matches[1] }
    }
}

function Set-EnvInteractively {
    $lines = New-Object System.Collections.Generic.List[string]
    $setKeys = @()
    $blankKeys = @()

    Write-Host ''
    Write-Host 'Press Enter to keep the value shown in [brackets], or enter 1 to leave it blank.'
    foreach ($line in Get-Content $EnvFile) {
        if ($line -notmatch '^([A-Za-z_][^=]*)=(.*)$') {
            $lines.Add($line)
            continue
        }
        $key = $Matches[1]
        $default = $Matches[2]

        if ($key -eq 'DJANGO_SECRET_KEY') {
            $value = Read-Host "$key [Enter = generate a new key]"
            if ($value -eq '') {
                # Single quotes keep characters like # and $ literal for dotenv.
                $default = "'$(New-SecretKey)'"
                Write-Host 'Generated a new secret key.'
            }
        } else {
            $value = Read-Host "$key [$default]"
        }

        if ($value -eq '1') {
            $value = ''
            $blankKeys += $key
        } elseif ($value -eq '') {
            $value = $default
            $setKeys += $key
        } else {
            $setKeys += $key
        }
        $lines.Add("$key=$value")
    }

    # Write UTF-8 without a BOM so the first key is read correctly by dotenv.
    [System.IO.File]::WriteAllLines($EnvFile, $lines, (New-Object System.Text.UTF8Encoding $false))

    Write-Host ''
    Write-Host "Saved $EnvFile"
    Write-Host "  Set: $(if ($setKeys) { $setKeys -join ' ' } else { '(none)' })"
    Write-Host "  Left blank: $(if ($blankKeys) { $blankKeys -join ' ' } else { '(none)' })"
}

function Initialize-EnvFile {
    Write-Host ''
    if (-not (Test-Path $EnvExample)) {
        Write-Host "Error: $EnvExample was not found."
        return
    }

    if (Test-Path $EnvFile) {
        if (-not (Confirm-Continue 'backend/.env already exists. Overwrite it?')) {
            Write-Host 'Keeping the existing backend/.env.'
            return
        }
    }

    Copy-Item $EnvExample $EnvFile -Force
    Write-Host 'The env file has been set up at backend/.env and is ready to be filled out.'
    Write-Host ''
    Write-Host 'How would you like to fill it out?'
    Write-Host '  1) Manually (edit backend/.env yourself)'
    Write-Host '  2) Be prompted for each value'
    while ($true) {
        $choice = Read-Host 'Enter 1 or 2'
        if ($choice -eq '1') {
            Write-Host "Open $EnvFile in your editor and replace the placeholder values."
            return
        }
        if ($choice -eq '2') { break }
        Write-Host 'Invalid choice.'
    }

    Write-Host ''
    Write-Host 'You will be asked for the following values:'
    foreach ($key in Get-EnvKeys $EnvFile) {
        Write-Host "  - $key"
    }
    Write-Host ''
    if (-not (Confirm-Continue 'Do you wish to continue?')) {
        Write-Host "Open $EnvFile in your editor and replace the placeholder values."
        return
    }

    Set-EnvInteractively
}

function Show-NextSteps {
    Write-Host @'

==================================================
  Setup complete
==================================================
To start the backend, run these from the repository root:
  .\.venv\Scripts\Activate.ps1
  cd backend
  python manage.py check
  python manage.py migrate
  python manage.py runserver

If PowerShell says running scripts is disabled when activating, run this
first in the same terminal:
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

check and migrate need your real MONGODB_URI in backend/.env.
Then open http://127.0.0.1:8000/api/health/ in your browser.
It should show {"status":"ok"}. Stop the server with Ctrl+C.

To run the game:
  1. Open Godot and click Import.
  2. Choose game/project.godot from this repository.
  3. Press F5 to run the project.
==================================================
'@
}

Invoke-GodotStep

if (Show-Prompt $VenvTitle $VenvPrompt) {
    Initialize-Venv
} else {
    Write-Host 'Skipping virtual environment setup.'
}

if (Show-Prompt $EnvTitle $EnvPrompt) {
    Initialize-EnvFile
} else {
    Write-Host 'Skipping env file setup.'
}

Show-NextSteps
