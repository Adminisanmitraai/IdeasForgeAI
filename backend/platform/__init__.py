"""IdeasForgeAI platform contracts and adapters.

FOS-BE-1 introduces dependency boundaries only. Existing implementations remain
the source of truth until compatibility adapters are connected.
"""

from .cross_product_router import (
    CROSS_PRODUCT_ROUTER_VERSION,
    CrossProductRouteDecision,
    CrossProductRouteRequest,
    RouteState,
    decide_cross_product_route,
)

__all__ = [
    "CROSS_PRODUCT_ROUTER_VERSION",
    "CrossProductRouteDecision",
    "CrossProductRouteRequest",
    "RouteState",
    "decide_cross_product_route",
]
