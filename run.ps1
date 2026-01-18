# Simple runner script for dotfiles installation using uv on Windows

# Check if uv is installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv is not installed. Installing uv..."
    # Install uv using the official installer
    Invoke-WebRequest -UseBasicParsing https://astral.sh/uv/install.ps1 | Invoke-Expression
}

# Ensure latest production Python is installed
uv python install --latest

# Run the dotfiles script with uv using latest Python
uv run --python latest dotfiles.py $args
