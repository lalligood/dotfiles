# Dotfiles Installation Script

This project installs various CLI tools and provides preferred configurations for them.

## Quick Start

### Using uv (Recommended)

The simplest way to run this script is using `uv`, which will automatically handle Python dependencies:

**On Linux/Mac:**

```bash
# If uv is not installed, it will be installed automatically
./run.sh [commands]

# Or manually:
uv run dotfiles.py [commands]
```

**On Windows (PowerShell):**

```powershell
# If uv is not installed, it will be installed automatically
.\run.ps1 [commands]

# Or manually:
uv run dotfiles.py [commands]
```

### Installing uv

If you don't have `uv` installed:

**Linux/Mac:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Available Commands

- `baseline` - Install core environment & CLI apps (Mac/Linux only)
- `bash` - Update bash shell and configure (Mac/Linux only)
- `iterm2` - Install iTerm2 with instructions (Mac only)
- `psql` - Install psql CLI (Linux only)
- `starship` - Install starship prompt (Mac/Linux only)
- `tmux` - Install tmux (Mac/Linux only)
- `vim` - Install GVim/MacVim/vim with personalized settings and font
- `vscode` - Open VSCode download page

### Examples

Install vim on any platform:

```bash
uv run dotfiles.py vim
```

Install multiple tools at once:

```bash
uv run dotfiles.py vim starship tmux
```

## Platform Support

- **Mac OSX**: Full support for all commands
- **Linux (Ubuntu)**: Full support for most commands
- **Windows**: Currently supports vim/gvim installation and configuration

### Windows Support

On Windows, the script will:

- Install vim/gvim using winget (or chocolatey if available)
- Copy `windows/_gvimrc` and `windows/_vimrc` to your home directory as `_gvimrc` and `_vimrc`
- Install Hack Nerd Font to the Windows Fonts directory

## Dependencies

Dependencies are managed via `uv` using `pyproject.toml`. The script requires:

- Python 3.11+ (uv automatically uses the latest production version)
- `click`
- `requests`

These are automatically installed when using `uv run`. The runner scripts ensure
the latest production Python is installed and used.

## Project Structure

```bash
.
├── dotfiles.py          # Main installation script
├── pyproject.toml       # Python dependencies (for uv)
├── run.sh               # Linux/Mac runner script
├── run.ps1              # Windows PowerShell runner script
├── _gvimrc              # GVim config (Mac/Linux)
├── _vimrc               # Vim config (Mac/Linux)
├── windows/
│   ├── _gvimrc          # GVim config for Windows
│   └── _vimrc           # Vim config for Windows
└── [other config files]
```
