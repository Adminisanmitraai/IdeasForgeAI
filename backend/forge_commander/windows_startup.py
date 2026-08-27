from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from .startup import StartupDescriptor, validate_startup_descriptor

FORGE_COMMANDER_WINDOWS_STARTUP_VERSION = "forge-commander.windows-startup.v1"


@dataclass(frozen=True, slots=True)
class WindowsStartupArtifact:
    startup_id: str
    launcher_path: str
    launcher_content: str
    mode: str = "user_startup"
    contract_version: str = FORGE_COMMANDER_WINDOWS_STARTUP_VERSION


def build_user_startup_artifact(
    descriptor: StartupDescriptor, *, launcher_path: str
) -> WindowsStartupArtifact:
    validate_startup_descriptor(descriptor)
    if descriptor.mode != "user_startup":
        raise ValueError("only user_startup is supported by this artifact builder")
    quoted_args = " ".join(f'"{arg}"' for arg in descriptor.arguments)
    launcher = (
        "@echo off\r\n"
        f"cd /d \"{descriptor.working_directory}\"\r\n"
        f"start \"ForgeCommander\" \"{descriptor.executable}\" {quoted_args}\r\n"
    )
    digest = sha256(
        f"{descriptor.device_id}\n{launcher_path}\n{launcher}".encode("utf-8")
    ).hexdigest()[:20]
    return WindowsStartupArtifact(
        startup_id=f"fc-winstart-{digest}",
        launcher_path=str(Path(launcher_path)),
        launcher_content=launcher,
    )


def validate_launcher_target(artifact: WindowsStartupArtifact) -> WindowsStartupArtifact:
    if not artifact.launcher_path.lower().endswith((".cmd", ".bat")):
        raise ValueError("launcher_path must end in .cmd or .bat")
    if "start \"ForgeCommander\"" not in artifact.launcher_content:
        raise ValueError("launcher content is missing ForgeCommander start command")
    return artifact


__all__ = [
    "FORGE_COMMANDER_WINDOWS_STARTUP_VERSION",
    "WindowsStartupArtifact",
    "build_user_startup_artifact",
    "validate_launcher_target",
]
