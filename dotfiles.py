#!/usr/bin/env python3
"""Create all necessary symlinks for personalized iTerm (Mac only), psql, tmux, &
vim settings. It will use `git clone` to acquire any pertinent files (such as Hack
font) as well.

This script requires that you are running on Linux or Mac, have at least Python 3.6
installed & have pip installed click."""
import click
from git import Repo
from pathlib import Path
import os
import subprocess
import sys

home = Path.home()
project_home = home / "Projects"
current_dir = Path.cwd()
vim_sources = [".gvimrc", ".vimrc", ".vim/"]
hack_repo = "source-foundry/Hack"


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
    print(f"Valid OS found: {current_os}")
    return current_os


def create_symlink(source_file: str, target_path: Path = home) -> None:
    """Create a symlink in expected directory for specified file."""
    source_path = current_dir / source_file
    target_file = target_path / source_file
    # Remove any existing symlink
    if target_file.is_symlink():
        target_file.unlink()
    # Change file extension if matching file exists
    if target_file.is_file():
        new_target = target_file.with_suffix(".bak")
        target_file.rename(new_target)
    target_file.symlink_to(source_path)
    print(f"Symlink for {source_path} successfully created in {target_path}")


def git_clone(project: str, target: Path = project_home) -> None:
    """Clone a git repository from GitHub."""
    target_path = project_home / project.split("/")[1]
    if not target_path.exists():
        print(f"Cloning {project}. This may take a minute or two. . .")
        Repo.clone_from(f"https://github.com/{project}.git", target_path)
        print(f"{project} cloned successfully to {target_path}")
    else:
        print(f"{target_path} already exists. Skipping. . .")


def exit_code(command: str) -> bool:
    """Check the exit code to see if application is installed or not."""
    try:
        _exit_code = subprocess.run(command.split())
    except FileNotFoundError:
        return False
    return True if _exit_code.returncode == 0 else False


def linux_install(application: str) -> None:
    """Install application on Linux."""
    if application.startswith("starship"):
        os.system("""sh -c '$(curl -fsSL https://starship.rs/install.sh)'""")
    else:
        application = (
            "postgresql-client-common"
            if application.startswith("psql")
            else application
        )
        os.system(f"sudo apt install {application}")


def mac_install(application: str) -> None:
    """Install application on Mac."""
    os.system("brew update")
    os.system(f"brew install {application}")


def check_for_install(command: str, current_os: str) -> None:
    """Determine if specified application is installed. Install if not found."""
    if exit_code(command) is False:
        if current_os == "linux":
            print(
                f"{command} does not appear to be installed. You may be prompted "
                + "to enter sudo password."
            )
            linux_install(command)
        else:
            mac_install(command)
    else:
        print(f"{command.split()[0]} already installed. Skipping. . .")


@click.command()
@click.option(
    "--project",
    "project_home",
    default=project_home,
    show_default=True,
    help="Specify path to your projects directory",
)
@click.option(
    "--iterm2",
    "iterm2",
    is_flag=True,
    default=False,
    help="Configure ONLY settings for iTerm 2 (Mac only!)",
)
@click.option(
    "--psql",
    "psql",
    is_flag=True,
    default=False,
    help="Configure ONLY settings for psql",
)
@click.option(
    "--tmux",
    "tmux",
    is_flag=True,
    default=False,
    help="Configure ONLY settings for tmux",
)
@click.option(
    "--vim",
    "vim",
    is_flag=True,
    default=False,
    help="Configure ONLY settings for vim",
)
@click.option(
    "--starship",
    "starship",
    is_flag=True,
    default=False,
    help="Install ONLY starship prompt with personal settings",
)
@click.option(
    "--all",
    "everything",
    is_flag=True,
    default=False,
    help="Install all configuration files for the current operating system",
)
def main(
    project_home: Path,
    iterm2: bool = False,
    psql: bool = False,
    tmux: bool = False,
    vim: bool = False,
    starship: bool = False,
    everything: bool = False,
) -> None:
    """Install all necessary personal configuration files for iTerm2 (Mac only),
    psql, tmux, vim, and starship."""
    running_on = determine_os()
    # Confirm the path where we expect the projects to be is a child dir of home
    # directory
    if home in list(current_dir.parents) and Path(project_home).exists():
        print(f"Projects directory found in {project_home}")
    else:
        print(
            "ERROR: PROJECTS DIRECTORY NOT FOUND IN HOME DIRECTORY OR DOES NOT "
            + "EXIST!"
        )
    if everything and running_on == "darwin":
        iterm2 = psql = tmux = vim = starship = True
    if everything:
        psql = tmux = vim = starship = True
    if iterm2 and running_on == "darwin":
        check_for_install("iterm2", running_on)
        # DO NOT SYMLINK iterm2 settings file!
        # create_symlink("com.google.code.iterm2.plist")
        print("Instructions for restoring iTerm2 settings...")
    elif iterm2:
        print("iterm2 CAN ONLY BE INSTALLED ON MAC OSX. Skipping. . .")
    if psql:
        create_symlink(".psqlrc")
    if tmux:
        check_for_install("tmux -V", running_on)
        create_symlink(f"{running_on}/.tmux.conf")
    if vim:
        # With vim directory, symlink should be ~/.vim!
        for each in vim_sources:
            target_path = home / ".vim" if each == "vim/" else home
            create_symlink(each, target_path)
        git_clone(hack_repo)
    if starship:
        check_for_install("starship --help", running_on)
        create_symlink("starship.toml", home / ".config")


if __name__ == "__main__":
    main()
