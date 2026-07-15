from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from backend.composition.container import PlatformServiceContainer

CONTRACT_VERSION: Final[str] = "composition.platform-registry.v1"

ContainerFactory = Callable[[], PlatformServiceContainer]


class PlatformRegistryConfigurationError(RuntimeError):
    pass


class PlatformRegistryNotConfiguredError(RuntimeError):
    pass


@dataclass(frozen=True)
class PlatformRegistryStatus:
    configured: bool
    initialized: bool
    contract_version: str = CONTRACT_VERSION


class PlatformServiceRegistry:
    """Thread-safe lazy holder for the shared platform service container.

    The registry owns no business capability and creates no legacy dependency
    itself. The application composition root supplies exactly one container
    factory. Interfaces may then resolve the same initialized service graph.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._factory: ContainerFactory | None = None
        self._container: PlatformServiceContainer | None = None

    def configure(
        self,
        factory: ContainerFactory,
        *,
        replace: bool = False,
    ) -> None:
        if not callable(factory):
            raise TypeError("Platform registry factory must be callable.")

        with self._lock:
            if self._factory is not None and not replace:
                raise PlatformRegistryConfigurationError(
                    "Platform service registry is already configured."
                )
            if self._container is not None and replace:
                raise PlatformRegistryConfigurationError(
                    "Initialized platform registry cannot be reconfigured."
                )
            self._factory = factory

    def get_container(self) -> PlatformServiceContainer:
        with self._lock:
            if self._container is not None:
                return self._container
            if self._factory is None:
                raise PlatformRegistryNotConfiguredError(
                    "Platform service registry is not configured."
                )

            container = self._factory()
            if not isinstance(container, PlatformServiceContainer):
                raise PlatformRegistryConfigurationError(
                    "Platform registry factory returned an invalid container."
                )
            self._container = container
            return container

    def status(self) -> PlatformRegistryStatus:
        with self._lock:
            return PlatformRegistryStatus(
                configured=self._factory is not None,
                initialized=self._container is not None,
            )

    def reset_for_tests(self) -> None:
        """Clear registry state for isolated tests only.

        Production code should configure the process registry once and never
        reset it while requests are running.
        """

        with self._lock:
            self._factory = None
            self._container = None


platform_service_registry = PlatformServiceRegistry()


def configure_platform_services(
    factory: ContainerFactory,
    *,
    replace: bool = False,
) -> None:
    platform_service_registry.configure(factory, replace=replace)


def get_platform_services() -> PlatformServiceContainer:
    return platform_service_registry.get_container()


def get_platform_registry_status() -> PlatformRegistryStatus:
    return platform_service_registry.status()
