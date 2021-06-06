#!/usr/bin/env python3
"""Create all necessary symlinks for personalized iTerm (Mac only), psql, tmux, &
vim settings. It will use `git clone` to acquire any pertinent files (such as Hack
font) as well.

This script requires that you are running on Linux or Mac, have at least Python 3.6
installed & have pip installed click."""
import click
import os
from pathlib import Path
import requests
import subprocess  # nosec
import sys
from zipfile import ZipFile

home = Path.home()
project_home = home / "Projects"
current_dir = Path.cwd()
currently_installed_list = {
    "darwin": ["brew", "list"],
    "linux": ["apt", "list", "--installed"],
}
vim_sources = [".gvimrc", ".vimrc", ".vim/"]
vim_apps = {"linux": "vim-gtk3", "darwin": "macvim"}
font_info = {"repo": "ryanoasis/nerd-fonts", "name": "Hack"}
font_destination = {"darwin": home / "Library" / "Fonts", "linux": home / ".fonts"}
package_manager = {"darwin": "brew", "linux": "sudo apt"}
apps = {
    "darwin": [
        "bash",
        "fzf",
        "git",
        "lazydocker",
        "most",
        "pipenv",
        "pspg",
        "the_silver_searcher",
        "yank",
    ],
    "linux": [
        "fzf",
        "git",
        # "lazydocker",
        "most",
        "pipenv",
        "pspg",
        "silversearcher-ag",
    ],
}
starship = {
    "darwin": "brew install starship",
    "linux": "sh -c '$(curl -fsSL https://starship.rs/install.sh)'",
}


class InvalidDirectoryError(Exception):
    """Raise this exception if trying to run this script from wrong directory."""

    pass


class InvalidOperatingSystemError(Exception):
    """Raise this exception whenever trying to run this script on Windows PC."""

    pass


def determine_os() -> str:
    """Determine the operating system that the script is being executed against."""
    current_os = sys.platform
    if current_os == "win32":  # GTFO!
        raise InvalidOperatingSystemError(
            "IS THIS SOME KIND OF SICK JOKE?! I DON'T DO WINDOWS!"
        )
    return current_os


def create_symlink(
    source_file: str, target_path: Path = home, override_target: bool = False
) -> None:
    """Create a symlink in expected directory for specified file."""
    source_path = current_dir / source_file
    target_file = target_path if override_target else (target_path / source_file)
    # Remove any existing symlink
    if target_file.is_symlink():
        target_file.unlink()
    # Change file extension if matching file exists
    if target_file.is_file():
        new_target = target_file.with_suffix(".bak")
        target_file.rename(new_target)
    target_file.symlink_to(source_path)
    print(f"Symlink for {source_path} successfully created in {target_file.parent}")


def download_and_install_font(font: str, download_path: Path = None) -> None:
    """Download latest version of Hack Nerd font from GitHub to local directory."""
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
    target_path = font_destination[determine_os()]
    target_path.mkdir(exist_ok=True)
    with ZipFile(zip_file_path, "r") as z:
        z.extractall(target_path)
    zip_file_path.unlink()  # Delete downloaded zip file


def exit_code(command: str) -> bool:
    """Check the exit code to see if application is installed or not."""
    try:
        _exit_code = subprocess.run(command.split(), capture_output=True)  # nosec
    except FileNotFoundError:
        return False
    return True if _exit_code.returncode == 0 else False


def linux_install(application: str) -> None:
    """Install application on Linux."""
    if application.startswith("starship"):
        os.system()  # nosec
    else:
        application = (
            "postgresql-client-common"
            if application.startswith("psql")
            else application
        )
        os.system("sudo apt update")  # nosec
        os.system(f"sudo apt install {application}")  # nosec


def mac_install(application: str) -> None:
    """Install application on Mac."""
    os.system("brew update")  # nosec
    os.system(f"brew install {application}")  # nosec


def check_for_install(
    command: str, mac_name: str = None, linux_name: str = None
) -> None:
    """Determine if specified application is installed. Install if not found."""
    if exit_code(command) is False:
        if determine_os() == "linux":
            print(
                f"{command} does not appear to be installed. You may be prompted "
                + "to enter sudo password."
            )
            linux_install(linux_name or command)
        else:
            mac_install(mac_name or command)
    else:
        print(f"{command.split()[0]} already installed. Skipping. . .")


@click.group()
def main() -> None:
    """Install all applications & necessary personal configuration files for:

    \b
    * bash -- shell
    * iTerm2 (Mac only) -- terminal emulator
    * psql -- PostgreSQL database CLI
    * starship -- prompt
    * tmux -- (t)erminal (mu)ltiple(x)er
    * vim/GVim/MacVim -- editor
    """
    if home in list(current_dir.parents) and Path(project_home).exists():
        print(f"Projects directory found in: {project_home}")
    else:
        raise InvalidDirectoryError(
            "ERROR: PROJECTS DIRECTORY NOT FOUND IN HOME DIRECTORY OR DOES NOT "
            + "EXIST!"
        )


@main.command()
def baseline():
    """Ensure that all core environment & CLI apps are installed. If any are
    missing, then this will install them for you."""
    installed_list = [
        each.split("/")[0]
        for each in subprocess.run(  # nosec
            currently_installed_list[determine_os()], capture_output=True
        )
        .stdout.decode()
        .split("\n")[1:-1]
    ]
    installer = package_manager[determine_os()].split()
    subprocess.run(installer + ["update"])  # nosec
    for each in apps[determine_os()]:
        if each not in installed_list:
            print(f"{each} NOT FOUND! Installing {each} now. . .")
            subprocess.run(installer + ["install", each])  # nosec
        else:
            print(f"{each} is already installed. Skipping. . .")


@main.command()
def bash():
    """Install bash shell with personalized settings."""
    if determine_os() == "darwin":
        check_for_install("bash")
        create_symlink(".bash_profile")
        # .bashrc is needed for starship prompt when inside pipenv shell
        create_symlink(".bashrc.mac", home / ".bashrc", override_target=True)
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
    create_symlink(".psqlrc")
    check_for_install("psql --version")


@main.command()
def vim():
    """Install GVim/MacVim with personalized settings and font."""
    for each in vim_sources:
        create_symlink(each)
    check_for_install("vim --version")
    download_and_install_font(font_info)


@main.command()
def tmux():
    """Install tmux with personalized settings."""
    running_on = determine_os()
    check_for_install("tmux -V")
    create_symlink(
        f"{running_on}/.tmux.conf", home / ".tmux.conf", override_target=True
    )


@main.command()
def starship():
    """Install starship prompt with personalized settings."""
    check_for_install("starship --help")
    create_symlink(".config/starship.toml")


@main.command()
def all():
    """Install ALL packages with personalized settings."""
    pass


if __name__ == "__main__":
    main()
