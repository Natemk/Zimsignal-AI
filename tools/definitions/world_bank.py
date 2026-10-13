"""Backward-compatible import for the World Bank client."""

from tools.public_data.world_bank import (
    IndicatorObservation,
    WorldBankNormalizedOutput,
    get_world_bank_indicator,
)

__all__ = [
    "IndicatorObservation",
    "WorldBankNormalizedOutput",
    "get_world_bank_indicator",
]
