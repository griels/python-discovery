from __future__ import annotations

import typing

from python_discovery._py_spec import BasePythonSpec


class UVNormalizer:
    _OS_MAP: typing.ClassVar[typing.Mapping[str, str]] = {
        "darwin": "macos",
        "win32": "windows",
    }
    _LIBC_MAP: typing.ClassVar[typing.Mapping[str, typing.Mapping[str, str]]] = {
        "linux": {"glibc": "gnu", "musl": "musl", "": "gnu"}
    }
    _NOMACHINE_FALLBACK: typing.ClassVar[
        typing.Mapping[str, typing.Mapping[int, str]]
    ] = {"windows": {32: "x86", 64: "x86_64"}}

    @classmethod
    def normalise_os(cls, spec: BasePythonSpec) -> str | None:
        return cls._OS_MAP.get(spec.operating_system or "", spec.operating_system)

    @classmethod
    def normalise_isa(cls, spec: BasePythonSpec) -> str:
        uv_os = cls.normalise_os(spec) or ""
        machine_map = {
            "arm64": "aarch64",
            "aarch64": "aarch64",
            "amd64": "x86_64",
            "x86_64": (
                {"macos": {32: "i686"}}.get(uv_os, {}).get(spec.architecture, "x86_64")
                if isinstance(spec.architecture, int)
                else "x86_64"
            ),
            "x86": {"windows": "x86"}.get(uv_os, "i686"),
            "i386": "i686",
            "i686": "i686",
        }
        machine_fallback = (
            cls._NOMACHINE_FALLBACK.get(uv_os, {}).get(spec.architecture, "")
            if isinstance(spec.architecture, int)
            else ""
        )
        base_python_machine = (spec.machine or "").lower()
        return machine_map.get(base_python_machine, machine_fallback)

    @classmethod
    def normalise_libc(cls, spec: BasePythonSpec):
        return cls._LIBC_MAP.get(spec.operating_system or "", {}).get(
            spec.libc or "", "none"
        )

    @classmethod
    def env_version_spec(cls, spec: BasePythonSpec) -> str:
        uv_imp = spec.implementation or ""
        free_threaded_tag = "+freethreaded" if spec.free_threaded else ""
        if not spec.major:  # pragma: win32 no cover
            version_spec = f"{uv_imp}"
        elif not spec.minor:
            version_spec = f"{uv_imp}{spec.major}{free_threaded_tag}"
        elif spec.architecture or spec.machine:

            uv_os = cls.normalise_os(spec) or ""

            uv_machine = cls.normalise_isa(spec)
            uv_libc = cls.normalise_libc(spec)
            version_spec = f"{uv_imp}-{spec.major}.{spec.minor}{free_threaded_tag}" + (
                f"-{uv_os}-{uv_machine}-{uv_libc}"
                if all([uv_machine, uv_os, uv_libc])
                else ""
            )
        else:
            version_spec = f"{uv_imp}{spec.major}.{spec.minor}{free_threaded_tag}"
        return version_spec
