"""Configuration models for roulette sessions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionConfig:
    max_spins: int = 200
    stop_loss: float | None = None
    profit_target: float | None = None
    table_minimum: float = 1.0
    table_maximum: float = 1_000.0

    def __post_init__(self) -> None:
        if self.max_spins <= 0:
            raise ValueError("max_spins must be positive.")
        if self.table_minimum <= 0:
            raise ValueError("table_minimum must be positive.")
        if self.table_maximum < self.table_minimum:
            raise ValueError("table_maximum must be greater than or equal to table_minimum.")
        if self.stop_loss is not None and self.stop_loss < 0:
            raise ValueError("stop_loss cannot be negative.")
        if self.profit_target is not None and self.profit_target <= 0:
            raise ValueError("profit_target must be positive when set.")
