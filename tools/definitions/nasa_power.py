"""Backward-compatible import for the NASA POWER client."""

from tools.public_data.nasa_power import (
    AgroclimateNormalizedOutput,
    get_agroclimate_history,
)

__all__ = ["AgroclimateNormalizedOutput", "get_agroclimate_history"]
