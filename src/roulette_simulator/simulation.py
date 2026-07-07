"""Monte Carlo orchestration for roulette sessions."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .configuration import SessionConfig
from .player import Player
from .session import RouletteSession
from .strategies import BettingStrategy
from .wheel import WheelType, RouletteWheel


@dataclass
class MonteCarloSimulation:
    strategy: BettingStrategy
    config: SessionConfig
    starting_bankroll: float
    base_unit: float
    wheel_type: WheelType = "american"
    number_of_simulations: int = 1_000
    seed: int | None = None

    def __post_init__(self) -> None:
        if self.number_of_simulations <= 0:
            raise ValueError("number_of_simulations must be positive.")

    def run(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Run independent sessions and return spin-level and session-level data."""

        spin_rows: list[dict] = []
        session_rows: list[dict] = []
        for simulation_id in range(1, self.number_of_simulations + 1):
            session_seed = None if self.seed is None else self.seed + simulation_id - 1
            player = Player(
                starting_bankroll=self.starting_bankroll,
                base_unit=self.base_unit,
            )
            wheel = RouletteWheel(wheel_type=self.wheel_type, seed=session_seed)
            session = RouletteSession(
                player=player,
                wheel=wheel,
                strategy=self.strategy,
                config=self.config,
                simulation_id=simulation_id,
                seed=session_seed,
            )
            result = session.run()
            spin_rows.extend(result.spins)
            session_rows.append(result.summary)
        return pd.DataFrame(spin_rows), pd.DataFrame(session_rows)
