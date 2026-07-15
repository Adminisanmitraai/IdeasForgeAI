"""Application composition helpers for IdeasForgeAI platform services."""

from .container import (
    LegacyTerminalDependencies,
    PlatformServiceContainer,
    build_terminal_platform_container,
)
from .registry import (
    PlatformRegistryConfigurationError,
    PlatformRegistryNotConfiguredError,
    PlatformRegistryStatus,
    PlatformServiceRegistry,
    configure_platform_services,
    get_platform_registry_status,
    get_platform_services,
    platform_service_registry,
)

__all__ = [
    "LegacyTerminalDependencies",
    "PlatformRegistryConfigurationError",
    "PlatformRegistryNotConfiguredError",
    "PlatformRegistryStatus",
    "PlatformServiceContainer",
    "PlatformServiceRegistry",
    "build_terminal_platform_container",
    "configure_platform_services",
    "get_platform_registry_status",
    "get_platform_services",
    "platform_service_registry",
]
