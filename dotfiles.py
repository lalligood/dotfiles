#!/usr/bin/env python3
"""Install all personal applications & provide all personal configurations."""

import click
from pathlib import Path
import requests
import subprocess
import sys
from typing import Optional
import webbrowser
from zipfile import ZipFile

home = Path.home()
project_home = home / "Projects"
current_dir = Path.cwd()
currently_installed_list = {
    "darwin": ["brew", "list"],
    "linux": ["apt", "list", "--installed"],
    "snap": ["snap", "list"],
}
font_info = {
    "repo": "ryanoasis/nerd-fonts",
    "name": "Hack",
    "destination": {
        "darwin": home / "Library" / "Fonts",
        "linux": home / ".fonts",
    },
}
package_manager = {
    "darwin": "brew",
    "linux": "sudo apt",
    "snap": "sudo snap",
}
baseline_apps = {
    "both": [
        "duf",
        "lsd",
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
        "fd",
        "difftastic",
        "lazydocker",
        "the_silver_searcher",
        "yank",
    ],
    "linux": [
        "fdfind",
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
        "verify": "vim --version",
    },
}
snaps = {
    "Firefox": "firefox",
    "GitKraken": "gitkraken",
    "Slack": "slack",
    "Spotify": "spotify",
    "VLC": "vlc",
    "VSCode": "code",
    "Zoom": "zoom-client",
    "difftastic": "difftastic",
}
vim_sources = [".gvimrc", ".vimrc", ".vim"]
manual_installs = {
    "starship": "https://starship.rs",
    "zoxide": "https://raw.githubusercontent.com/ajeetdsouza/zoxide/main",
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


def create_symlink(source_file: str, target_path: Optional[Path] = None) -> None:
    """Create a symlink in expected directory for specified file."""
    source_path = current_dir / source_file
    target_file = target_path or (home / source_file)
    # Remove any existing symlink
    if target_file.is_symlink():
        target_file.unlink()
    # Change file extension if matching file exists
    if target_file.is_file():
        new_target = target_file.with_suffix(".bak")
        target_file.rename(new_target)
    tid = True if source_path.is_dir() else False
    target_file.symlink_to(source_path, target_is_directory=tid)
    print(f"Symlink for {source_path} successfully created in {target_file.parent}")


def download_and_install_font(
    font: dict, operating_system: str, download_path: Optional[Path] = None
) -> None:
    """Download latest version of Hack Nerd font from GitHub to local directory.

    If font already exists, it will download latest version & install it.
    """
    print("Checking for latest version of Hack Nerd font. This may take a few seconds.")
    repo = font["repo"]
    name = font["name"]
    destination = font["destination"]
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
    target_path = destination[operating_system]
    target_path.mkdir(exist_ok=True)
    with ZipFile(zip_file_path, "r") as z:
        z.extractall(target_path)
    zip_file_path.unlink()  # Delete downloaded zip file
    print(f"{name} font successfully installed in {target_path}")


def exit_code(command: str) -> bool:
    """Check the exit code to see if application is installed or not."""
    try:
        _exit_code = subprocess.run(command.split(), capture_output=True)
    except FileNotFoundError:
        return False
    return True if _exit_code.returncode == 0 else False


def bash_installer_for_linux(application_name: str, base_url: str) -> None:
    """LINUX ONLY: Download installer, install application, and delete installer."""
    install_file = "install.sh"
    url = f"{base_url}/{install_file}"
    target_file = project_home / install_file
    print(f"Downloading {application_name}")
    installer = requests.get(url, stream=True, allow_redirects=True, timeout=30)
    with open(target_file, "wb") as f:
        f.write(installer.content)
    print(f"Installing {application_name}. . .")
    subprocess.run(["sh", "-c", target_file])
    print(f"Deleting {target_file}")
    target_file.unlink()


def check_for_install(app_name: str, operating_system: str) -> None:
    """Determine if specified application is installed. Install if not found."""
    command = apps[app_name]["verify"]
    package_name = apps[app_name][operating_system]
    installer = package_manager[operating_system].split()
    installer.extend(["install", package_name])
    if exit_code(command):
        print(f"{app_name} already installed. Skipping. . .")
        return
    if operating_system == "linux" and package_name in manual_installs.keys():
        bash_installer_for_linux(package_name, manual_installs[package_name])
        return
    subprocess.run(installer)


@click.group(chain=True)
def main() -> None:
    r"""Install all applications & necessary personal configuration files for:

    \b
    * bash -- shell
    * iTerm2 (Mac only) -- terminal emulator
    * psql -- PostgreSQL database CLI
    * starship -- prompt
    * tmux -- (t)erminal (mu)ltiple(x)er
    * vim -- GVim/MacVim editor
    * VSCode -- IDE (open website only!)
    \b
    Some Linux applications should be installed as snaps, such as:
    \b
    * Firefox
    * GitKraken
    * Slack
    * Spotify
    * VLC
    * VSCode
    * Zoom
    * difftastic
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
    """Ensure that all core environment & CLI apps are installed.

    If any are missing, then this will install them.
    """
    platform = determine_os()
    installed_list = [
        each.split("/")[0]
        for each in subprocess.run(
            currently_installed_list[platform], capture_output=True
        )
        .stdout.decode()
        .split("\n")[1:-1]
    ]
    installer = package_manager[platform].split()
    baseline_candidates = baseline_apps["both"] + baseline_apps[platform]
    for each in baseline_candidates:
        if each not in installed_list:
            print(f"{each} NOT FOUND! Installing {each} now. . .")
            subprocess.run(installer.extend(["install", each]))
            if determine_os() == "darwin":
                if each == "fzf":
                    subprocess.run(["/usr/local/opt/fzf/install"])
                if each == "difftastic":
                    subprocess.run(["git config --global diff.external difft"])
        else:
            print(f"{each} is already installed. Skipping. . .")


@main.command()
def bash():
    """Update bash shell if necessary & configure with personalized settings."""
    platform = determine_os()
    if platform == "darwin":
        check_for_install("bash", platform)
        create_symlink(".bash_profile")
        # .bashrc is ONLY needed for starship prompt when inside pipenv shell
        create_symlink(".bashrc.mac", home / ".bashrc")
    else:
        create_symlink(".bashrc")
    create_symlink(".bash_aliases")


@main.command()
def iterm2():
    """Install iTerm2 (Mac OSX ONLY) & provide instructions to load settings."""
    usage = """VERY IMPORTANT: READ ALL OF THIS BEFORE CONTINUING!!!

        *** INSTRUCTIONS FOR RESTORING iTerm2 SETTINGS ***
1. Open iTerm2.
2. Open Preferences (iTerm2 -> Preferences... OR <Cmd>-,)
3. Go to General tab. Then click on Preferences.
4. Ensure that "Load preferences from a custom folder or URL" is checked.
5. Click Browse & navigate to your dotfiles project folder containing
    com.googlecode.iterm2.plist file. Click Open."""
    platform = determine_os()
    if platform == "darwin":
        check_for_install("iterm2", platform)
        print(usage)
    else:
        print("iterm2 CAN ONLY BE INSTALLED ON MAC OSX. Skipping. . .")


@main.command()
def psql():
    """Install psql CLI for PostgreSQL with personalized settings."""
    platform = determine_os()
    check_for_install("psql", platform)
    create_symlink(".psqlrc")


@main.command()
def starship():
    """Install starship prompt with personalized settings."""
    platform = determine_os()
    check_for_install("starship", platform)
    create_symlink(".config/starship.toml")


@main.command()
def tmux():
    """Install tmux with personalized settings."""
    platform = determine_os()
    check_for_install("tmux", platform)
    current_os = "mac" if platform == "darwin" else platform
    create_symlink(f"{current_os}/.tmux.conf", home / ".tmux.conf")


@main.command()
def vim():
    """Install GVim/MacVim with personalized settings and font."""
    platform = determine_os()
    check_for_install("vim", platform)
    for each in vim_sources:
        create_symlink(each)
    download_and_install_font(font_info, platform)


@main.command()
def vscode():
    """Install VSCode for MacOSX by opening download page in web browser."""
    platform = determine_os()
    if platform == "darwin":
        print(
            "VSCode needs to be installed manually on Mac OSX. "
            "Opening download page in browser. . ."
        )
        webbrowser.open("https://code.visualstudio.com/Download")
    else:
        print("Run dotfiles with '--snap' option to install VSCode on Linux.")


@main.command()
def snap():
    """Allow selected applications to be installed on Linux via snap store."""
    platform = determine_os()
    if platform != "linux":
        print("Snaps can only be installed in Linux! Exiting . . .")
        sys.exit(1)
    # Ask user if they want all installed or select particular snaps to be installed
    for app_name, snap_name in snaps.items():
        print(f"Installing {app_name}. Enter 'sudo' password if prompted.")
        installer = package_manager["snap"].split()
        installer.extend(["install", snap_name])
        subprocess.run(installer)


if __name__ == "__main__":
    main()
