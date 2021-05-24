"""Tests for dotfiles.py."""
from pytest import mark, raises

from dotfiles import (
    InvalidOperatingSystemError,
    create_symlink,
    determine_os,
    exit_code,
)


def test_determine_os_returns_linux(capsys):
    """Make sure that Linux operating system is found."""
    result = determine_os()
    assert "linux" == result
    stdout, _ = capsys.readouterr()
    assert "Valid" in stdout


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


@mark.xfail(reason="INCOMPLETE")
def test_git_clone_adds_repo_to_Projects_directory():
    """Make sure that a project is cloned from GitHub to Projects directory."""
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
