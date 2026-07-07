"""Player bankroll model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Player:
    starting_bankroll: float
    base_unit: float
    bankroll: float | None = None

    def __post_init__(self) -> None:
        if self.starting_bankroll <= 0:
            raise ValueError("starting_bankroll must be positive.")
        if self.base_unit <= 0:
            raise ValueError("base_unit must be positive.")
        if self.bankroll is None:
            self.bankroll = self.starting_bankroll

    @property
    def net_profit(self) -> float:
        return float(self.bankroll or 0) - self.starting_bankroll

    def can_cover(self, amount: float) -> bool:
        return float(self.bankroll or 0) >= amount

    def apply_profit(self, profit: float) -> None:
        self.bankroll = max(0.0, float(self.bankroll or 0) + profit)
