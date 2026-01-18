#!/usr/bin/env python3
"""Create all necessary symlinks for personalized iTerm (Mac only), psql, tmux, &
vim settings. It will use `git clone` to acquire any pertinent files (such as Hack
font) as well.

This script requires that you are running on Linux, Mac, or Windows, have at least
Python 3.11 installed. Dependencies are managed via `uv`, which will automatically
use the latest production version of Python."""

import click
from pathlib import Path
from typing import Optional
import os
import requests
import subprocess
import sys
import webbrowser
import shutil
from zipfile import ZipFile

home = Path.home()
project_home = home / "Projects"
current_dir = Path.cwd()
currently_installed_list = {
    "darwin": ["brew", "list"],
    "linux": ["apt", "list", "--installed"],
    "win32": None,  # Windows package management handled differently
}
font_info = {"repo": "ryanoasis/nerd-fonts", "name": "Hack"}
if sys.platform == "win32":
    localappdata = os.environ.get("LOCALAPPDATA", "")
    font_destination = {
        "darwin": home / "Library" / "Fonts",
        "linux": home / ".fonts",
        "win32": Path(localappdata) / "Microsoft" / "Windows" / "Fonts"
        if localappdata
        else None,
    }
else:
    font_destination = {
        "darwin": home / "Library" / "Fonts",
        "linux": home / ".fonts",
    }
package_manager = {"darwin": "brew", "linux": "sudo apt", "win32": None}
baseline_apps = {
    "both": [
        "duf",
        "exa",
        "fzf",
        "git",
        "lynx",
        "pandoc",
        "most",
        "pipenv",
        "pspg",
    ],
    "darwin": [
        "bash",
        "difftastic",
        "lazydocker",
        "the_silver_searcher",
        "yank",
    ],
    "linux": [
        # "lazydocker",
        "silversearcher-ag",
    ],
}
apps = {
    "bash": {
        "darwin": "bash",
        "verify": "bash",
    },
    "psql": {
        "linux": "postgresql-client-common",
        "verify": "psql --version",
    },
    "starship": {
        "darwin": "starship",
        "linux": "starship",
        "verify": "starship --help",
    },
    "tmux": {
        "darwin": "tmux",
        "linux": "tmux",
        "verify": "tmux -V",
    },
    "vim": {
        "darwin": "macvim",
        "linux": "vim-gtk3",
        "win32": "vim",
        "verify": "vim --version",
    },
}
vim_sources = [".gvimrc", ".vimrc", ".vim"]


class InvalidDirectoryError(Exception):
    """Raise this exception if trying to run this script from wrong directory."""

    pass


class InvalidOperatingSystemError(Exception):
    """Raise this exception when trying to use an unsupported feature on Windows."""

    pass


def determine_os() -> str:
    """Determine the operating system that the script is being executed against."""
    current_os = sys.platform
    return current_os


def create_symlink(source_file: str, target_path: Optional[Path] = None) -> None:
    """Create a symlink (or copy on Windows) in expected directory for specified file."""
    source_path = current_dir / source_file
    if not source_path.exists():
        print(f"Warning: Source file {source_path} does not exist. Skipping...")
        return
    target_file = target_path or (home / source_file)
    current_os = determine_os()

    # Remove any existing symlink or file
    if target_file.is_symlink():
        target_file.unlink()
    elif target_file.is_file() or target_file.is_dir():
        # Create backup of existing file
        new_target = target_file.with_suffix(target_file.suffix + ".bak")
        if new_target.exists():
            if new_target.is_dir():
                shutil.rmtree(new_target)
            else:
                new_target.unlink()
        if target_file.is_dir():
            shutil.move(str(target_file), str(new_target))
        else:
            target_file.rename(new_target)
        print(f"Backed up existing {target_file} to {new_target}")

    # On Windows, use copy instead of symlink for better compatibility
    if current_os == "win32":
        if source_path.is_dir():
            shutil.copytree(str(source_path), str(target_file))
        else:
            shutil.copy2(str(source_path), str(target_file))
        print(f"Copied {source_path} to {target_file}")
    else:
        tid = True if source_path.is_dir() else False
        target_file.symlink_to(source_path, target_is_directory=tid)
        print(f"Symlink for {source_path} successfully created in {target_file.parent}")


def download_and_install_font(font: dict, download_path: Optional[Path] = None) -> None:
    """Download latest version of Hack Nerd font from GitHub to local directory. If font
    already exists, it will download latest version & install it."""
    current_os = determine_os()
    if current_os == "win32" and font_destination.get("win32") is None:
        print(
            "Warning: Cannot determine Windows font directory. Skipping font installation."
        )
        return

    print("Checking for latest version of Hack Nerd font. This may take a few seconds.")
    repo = font.get("repo")
    name = font.get("name")
    latest_url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(latest_url).json()
    version = response.get("tag_name")
    print(f"Latest version is {version}. Please wait while downloading fonts now.")
    zip_file_url = f"https://github.com/{repo}/releases/download/{version}/{name}.zip"
    download_path = download_path or project_home
    zip_file_path = download_path / f"{name}.zip"
    print(f"Please wait while downloading {zip_file_path}. . .")
    with requests.get(zip_file_url, stream=True) as r, open(zip_file_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    target_path = font_destination[current_os]
    if target_path:
        target_path.mkdir(parents=True, exist_ok=True)
        with ZipFile(zip_file_path, "r") as z:
            z.extractall(target_path)
        zip_file_path.unlink()  # Delete downloaded zip file
        print(f"{name} font successfully installed in {target_path}")


def exit_code(command: str) -> bool:
    """Check the exit code to see if application is installed or not."""
    try:
        # Use shell=True on Windows for better command execution
        shell = sys.platform == "win32"
        _exit_code = subprocess.run(
            command if shell else command.split(),
            shell=shell,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False
    return True if _exit_code.returncode == 0 else False


def starship_installer_for_linux():
    """LINUX ONLY: Download installer, install starship prompt, and delete installer."""
    install_file = "install.sh"
    url = f"https://starship.rs/{install_file}"
    target_file = project_home / install_file
    print(f"Downloading {target_file}")
    installer = requests.get(url, stream=True, allow_redirects=True, timeout=30)
    with open(target_file, "wb") as f:
        f.write(installer.content)
    print("Installing starship. . .")
    subprocess.run(["sh", "-c", target_file])
    print(f"Deleting {target_file}")
    target_file.unlink()


def check_for_install(app_name: str) -> None:
    """Determine if specified application is installed. Install if not found."""
    current_os = determine_os()
    command = apps[app_name]["verify"]
    if exit_code(command):
        print(f"{app_name} already installed. Skipping. . .")
    else:
        if current_os == "win32":
            _install_windows_app(app_name)
        else:
            installer_str = package_manager.get(current_os)
            if not installer_str:
                print(
                    f"Package manager not configured for {current_os}. Skipping {app_name}..."
                )
                return
            installer = installer_str.split()
            package_name = apps[app_name].get(current_os)
            if not package_name:
                print(f"{app_name} is not available for {current_os}. Skipping...")
                return
            if current_os == "linux" and package_name == "starship":
                starship_installer_for_linux()
            else:
                subprocess.run(installer + ["install", package_name])


def _install_windows_app(app_name: str) -> None:
    """Install applications on Windows using winget or chocolatey."""
    if app_name == "vim":
        # Try winget first (comes with Windows 10/11)
        winget_result = subprocess.run(
            [
                "winget",
                "install",
                "vim.vim",
                "--silent",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ],
            capture_output=True,
        )
        if winget_result.returncode == 0:
            print("Installed vim using winget")
            return

        # Fall back to chocolatey if available
        choco_result = subprocess.run(
            ["choco", "install", "vim", "-y"],
            capture_output=True,
        )
        if choco_result.returncode == 0:
            print("Installed vim using chocolatey")
            return

        print(
            "Could not install vim automatically. Please install manually using:\n"
            "  winget install vim.vim\n"
            "  or\n"
            "  choco install vim"
        )
    else:
        print(
            f"Automatic installation of {app_name} on Windows is not yet implemented."
        )


@click.group(chain=True)
def main() -> None:
    """Install all applications & necessary personal configuration files for:

    \b
    * bash -- shell (Mac/Linux only)
    * iTerm2 (Mac only) -- terminal emulator
    * psql -- PostgreSQL database CLI (Linux only)
    * starship -- prompt (Mac/Linux only)
    * tmux -- (t)erminal (mu)ltiple(x)er (Mac/Linux only)
    * vim -- GVim/MacVim editor
    * VSCode -- IDE (open website only!)
    """
    # On Windows, project_home check is optional
    current_os = determine_os()
    if current_os == "win32":
        # Just check that we're in a reasonable location
        print(f"Running on Windows. Project directory: {current_dir}")
    elif home in list(current_dir.parents) and Path(project_home).exists():
        print(f"Projects directory found in: {project_home}")
    else:
        raise InvalidDirectoryError(
            "ERROR: PROJECTS DIRECTORY NOT FOUND IN HOME DIRECTORY OR DOES NOT "
            + "EXIST!"
        )


@main.command()
def baseline():
    """Ensure that all core environment & CLI apps are installed. If any are missing,
    then this will install them."""
    current_os = determine_os()
    if current_os == "win32":
        print("Baseline installation is not yet fully implemented for Windows.")
        print("Please install applications manually or use individual commands.")
        return

    installed_list = [
        each.split("/")[0]
        for each in subprocess.run(
            currently_installed_list[current_os], capture_output=True
        )
        .stdout.decode()
        .split("\n")[1:-1]
    ]
    installer = package_manager[current_os].split()
    baseline_candidates = baseline_apps["both"] + baseline_apps.get(current_os, [])
    for each in baseline_candidates:
        if each not in installed_list:
            print(f"{each} NOT FOUND! Installing {each} now. . .")
            subprocess.run(installer + ["install", each])
            if current_os == "darwin":
                if each == "fzf":
                    subprocess.run(["/usr/local/opt/fzf/install"])
                if each == "difftastic":
                    subprocess.run(["git config --global diff.external difft"])
        else:
            print(f"{each} is already installed. Skipping. . .")


@main.command()
def bash():
    """Update bash shell to latest version if necessary and configure with personalized
    settings."""
    if determine_os() == "darwin":
        check_for_install("bash")
        create_symlink(".bash_profile")
        # .bashrc is ONLY needed for starship prompt when inside pipenv shell
        create_symlink(".bashrc.mac", home / ".bashrc")
    else:
        create_symlink(".bashrc")
    create_symlink(".bash_aliases")


@main.command()
def iterm2():
    """Mac OSX ONLY: Install iTerm2 & provide instructions to load preferred
    settings."""
    usage = """VERY IMPORTANT: READ ALL OF THIS BEFORE CONTINUING!!!

        *** INSTRUCTIONS FOR RESTORING iTerm2 SETTINGS ***
1. Open iTerm2.
2. Open Preferences (iTerm2 -> Preferences... OR <Cmd>-,)
3. Go to General tab. Then click on Preferences.
4. Ensure that "Load preferences from a custom folder or URL" is checked.
5. Click Browse & navigate to your dotfiles project folder containing
    com.googlecode.iterm2.plist file. Click Open."""
    if determine_os() == "darwin":
        check_for_install("iterm2")
        print(usage)
    else:
        print("iterm2 CAN ONLY BE INSTALLED ON MAC OSX. Skipping. . .")


@main.command()
def psql():
    """Install psql CLI for PostgreSQL with personalized settings."""
    check_for_install("psql")
    create_symlink(".psqlrc")


@main.command()
def starship():
    """Install starship prompt with personalized settings."""
    check_for_install("starship")
    create_symlink(".config/starship.toml")


@main.command()
def tmux():
    """Install tmux with personalized settings."""
    check_for_install("tmux")
    current_os = "mac" if determine_os() == "darwin" else determine_os()
    create_symlink(f"{current_os}/.tmux.conf", home / ".tmux.conf")


@main.command()
def vim():
    """Install GVim/MacVim with personalized settings and font."""
    current_os = determine_os()
    check_for_install("vim")

    if current_os == "win32":
        # On Windows, use the files from windows/ directory and rename them
        windows_gvimrc = current_dir / "windows" / "_gvimrc"
        windows_vimrc = current_dir / "windows" / "_vimrc"

        if windows_gvimrc.exists():
            # Windows uses _gvimrc and _vimrc (with underscore) in home directory
            create_symlink("windows/_gvimrc", home / "_gvimrc")
        else:
            print(
                f"Warning: {windows_gvimrc} not found. Skipping _gvimrc installation."
            )

        if windows_vimrc.exists():
            create_symlink("windows/_vimrc", home / "_vimrc")
        else:
            print(f"Warning: {windows_vimrc} not found. Skipping _vimrc installation.")
    else:
        # On Unix-like systems, use .gvimrc, .vimrc, and .vim
        for each in vim_sources:
            create_symlink(each)

    download_and_install_font(font_info)


@main.command()
def vscode():
    """Open download page in web browser for VSCode."""
    print("Opening download page in browser. . .")
    webbrowser.open("https://code.visualstudio.com/Download")


if __name__ == "__main__":
    main()
