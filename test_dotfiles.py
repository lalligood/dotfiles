"""Tests for dotfiles.py."""
from pathlib import Path
from pytest import mark, raises
import sys

from dotfiles import (
    InvalidOperatingSystemError,
    determine_os,
    exit_code,
    font_info,
    download_and_install_font,
)


def test_determine_os_passes_with_current_os():
    """Make sure that current operating system is found."""
    result = determine_os()
    assert sys.platform == result


@mark.xfail(reason="Need to mock out sys.platform call")
def test_determine_os_fails_on_windows():
    """Make sure that custom exception is raised when running on Windows PC."""
    with raises(InvalidOperatingSystemError):
        pass


@mark.xfail(reason="INCOMPLETE")
def test_create_symlink_creates_new_link():
    """Create a new symlink in the user home directory without overwriting an
    existing symlink or file."""
    # Create empty file in temporary location
    # result = create_symlink()
    pass


@mark.xfail(reason="INCOMPLETE")
def test_create_symlink_replaces_existing_symlink():
    """Create a new symlink in the user home directory without overwriting an
    existing symlink or file."""
    # Create empty file in temporary location
    # result = create_symlink()
    pass


@mark.xfail(reason="INCOMPLETE")
def test_create_symlink_creates_backup_of_file():
    """Create a new symlink in the user home directory without overwriting an
    existing symlink or file."""
    # Create empty file in temporary location
    # result = create_symlink()
    pass


@mark.parametrize(
    "command, expected",
    [("tmux -V", True), ("psql", False), ("asdfasdfasdfasdf", False)],
    ids=["already_installed", "not_installed", "does_not_exist"],
)
def test_exit_code_detects_installed_application(command, expected):
    """Make sure that True is returned when an application has already been
    installed."""
    result = exit_code(command)
    assert result is expected


def test_download_and_install_font_success(tmpdir, capsys):
    """Make sure that zip file containing fonts is downloaded.

    WARNING: This test will overwrite existing fonts!"""
    download_and_install_font(font_info, Path(tmpdir))
    stdout, _ = capsys.readouterr()
    assert "Hack.zip" in stdout
