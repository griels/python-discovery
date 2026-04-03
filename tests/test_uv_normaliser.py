from __future__ import annotations


import sys

import pytest

from python_discovery._uv._normalizer import UVNormalizer
from python_discovery._py_spec import BasePythonSpec


def test_env_version_spec_no_architecture() -> None:
    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        architecture=None,
        operating_system="win32",
    )

    assert UVNormalizer.env_version_spec(python_info) == "cpython3.11"


@pytest.mark.parametrize("architecture", [32, 64])
def test_env_version_spec_architecture_configured(architecture: int) -> None:
    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="win32",
        architecture=architecture,
    )

    uv_arch = {32: "x86", 64: "x86_64"}[architecture]
    assert (
        UVNormalizer.env_version_spec(python_info)
        == f"cpython-3.11-windows-{uv_arch}-none"
    )


def test_env_version_spec_architecture_configured_overwrite_sys_exe() -> (
    None
):  # pragma: win32 cover

    (major, minor) = sys.version_info[:2]
    python_info = BasePythonSpec(
        implementation="cpython",
        major=major,
        minor=minor,
        micro=0,
        architecture=32,
        operating_system="win32",
    )

    assert (
        UVNormalizer.env_version_spec(python_info)
        == f"cpython-{major}.{minor}-windows-x86-none"
    )


def test_env_version_spec_free_threaded() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=13,
        micro=3,
        operating_system="win32",
        free_threaded=True,
    )

    assert UVNormalizer.env_version_spec(python_info) == "cpython3.13+freethreaded"


def test_env_version_spec_machine_none() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="linux",
        architecture=None,
        machine=None,
    )

    assert UVNormalizer.env_version_spec(python_info) == "cpython3.11"


def test_env_version_spec_machine_none_with_architecture() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="linux",
        architecture=64,
        machine=None,
    )

    # When machine is None, uv_arch becomes empty and no os/arch/libc suffix is appended
    assert UVNormalizer.env_version_spec(python_info) == "cpython-3.11"


@pytest.mark.parametrize(
    ("machine", "expected_uv_arch"),
    [
        ("arm64", "aarch64"),
        ("aarch64", "aarch64"),
        ("amd64", "x86_64"),
        ("x86_64", "x86_64"),
        ("x86", "i686"),
        ("i386", "i686"),
        ("i686", "i686"),
    ],
)
def test_env_version_spec_machine_architecture_mapping(
    machine: str, expected_uv_arch: str
) -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="linux",
        architecture=64,
        machine=machine,
    )

    assert (
        UVNormalizer.env_version_spec(python_info)
        == f"cpython-3.11-linux-{expected_uv_arch}-gnu"
    )


def test_env_version_spec_machine_x86_64_macos_32bit() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="darwin",
        architecture=32,
        machine="x86_64",
    )

    # On macOS with 32-bit architecture, x86_64 maps to i686
    assert UVNormalizer.env_version_spec(python_info) == "cpython-3.11-macos-i686-none"


def test_env_version_spec_machine_x86_64_macos_64bit() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="darwin",
        architecture=64,
        machine="x86_64",
    )

    # On macOS with 64-bit architecture, x86_64 maps to x86_64
    assert (
        UVNormalizer.env_version_spec(python_info) == "cpython-3.11-macos-x86_64-none"
    )


def test_env_version_spec_machine_x86_64_macos_no_architecture() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="darwin",
        machine="x86_64",
    )

    # On macOS with no architecture specified, x86_64 maps to x86_64
    assert (
        UVNormalizer.env_version_spec(python_info) == "cpython-3.11-macos-x86_64-none"
    )


def test_no_minor() -> None:
    """
    Test that minor version is not included in environment version specification when not provided.
    """
    python_info = BasePythonSpec(implementation="cpython", major=3)
    assert UVNormalizer.env_version_spec(python_info) == "cpython3"
    python_info = BasePythonSpec(implementation="cpython", major=3, free_threaded=True)
    assert UVNormalizer.env_version_spec(python_info) == "cpython3+freethreaded"


def test_no_major() -> None:
    python_info = BasePythonSpec(implementation="cpython")
    assert UVNormalizer.env_version_spec(python_info) == "cpython"


def test_env_version_spec_machine_arm64_macos_32bit() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="darwin",
        architecture=32,
        machine="arm64",
    )

    # On macOS, arm64 always maps to aarch64 regardless of architecture setting
    assert (
        UVNormalizer.env_version_spec(python_info) == "cpython-3.11-macos-aarch64-none"
    )


def test_env_version_spec_machine_arm64_macos_64bit() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="darwin",
        architecture=64,
        machine="arm64",
    )

    # On macOS, arm64 always maps to aarch64 regardless of architecture setting
    assert (
        UVNormalizer.env_version_spec(python_info) == "cpython-3.11-macos-aarch64-none"
    )


def test_env_version_spec_machine_arm64_macos_no_architecture() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="darwin",
        architecture=None,
        machine="arm64",
    )

    # On macOS, arm64 always maps to aarch64 regardless of architecture setting
    assert (
        UVNormalizer.env_version_spec(python_info) == "cpython-3.11-macos-aarch64-none"
    )


def test_env_version_spec_libc_musl_linux() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="linux",
        libc="musl",
        machine="x86_64",
    )

    assert (
        UVNormalizer.env_version_spec(python_info) == "cpython-3.11-linux-x86_64-musl"
    )


def test_env_version_spec_libc_glibc_linux() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="linux",
        libc="glibc",
        machine="x86_64",
    )

    assert UVNormalizer.env_version_spec(python_info) == "cpython-3.11-linux-x86_64-gnu"


def test_env_version_spec_libc_windows() -> None:

    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="windows",
        libc="anything",
        machine="x86_64",
    )

    assert (
        UVNormalizer.env_version_spec(python_info) == "cpython-3.11-windows-x86_64-none"
    )


def test_env_version_spec_machine_x86_windows() -> None:
    python_info = BasePythonSpec(
        implementation="cpython",
        major=3,
        minor=11,
        micro=9,
        operating_system="windows",
        machine="x86",
    )
    assert UVNormalizer.env_version_spec(python_info) == "cpython-3.11-windows-x86-none"
