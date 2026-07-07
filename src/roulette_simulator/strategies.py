"""Betting strategies for roulette simulations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .bets import Bet, BetType
from .player import Player


@dataclass
class BettingStrategy(ABC):
    """Base class for stateful roulette strategies."""

    name: str = field(init=False)

    def reset(self) -> None:
        """Reset strategy state before a new independent session."""

    def record_result(self, profit: float) -> None:
        """Update strategy state after a completed spin."""

    @abstractmethod
    def get_bets(self, player: Player) -> list[Bet]:
        """Return bets for the next spin."""

    def _unit(self, player: Player, multiplier: float = 1.0) -> float:
        return player.base_unit * multiplier


@dataclass
class FlatRedStrategy(BettingStrategy):
    name: str = "FlatRedStrategy"

    def get_bets(self, player: Player) -> list[Bet]:
        return [Bet(BetType.RED, self._unit(player))]


@dataclass
class FlatBlackStrategy(BettingStrategy):
    name: str = "FlatBlackStrategy"

    def get_bets(self, player: Player) -> list[Bet]:
        return [Bet(BetType.BLACK, self._unit(player))]


@dataclass
class FlatDozenStrategy(BettingStrategy):
    dozen: int = 1
    name: str = "FlatDozenStrategy"

    def get_bets(self, player: Player) -> list[Bet]:
        return [Bet(BetType.DOZEN, self._unit(player), self.dozen)]


@dataclass
class BlackThirdZeroStrategy(BettingStrategy):
    """Bet black, the third dozen, and zero each spin."""

    name: str = "BlackThirdZeroStrategy"

    def get_bets(self, player: Player) -> list[Bet]:
        return [
            Bet(BetType.BLACK, self._unit(player) * 2),
            Bet(BetType.DOZEN, self._unit(player), 3),
            Bet(BetType.STRAIGHT, self._unit(player), 0),
        ]


@dataclass
class MartingaleRedStrategy(BettingStrategy):
    name: str = "MartingaleRedStrategy"
    loss_streak: int = 0

    def reset(self) -> None:
        self.loss_streak = 0

    def get_bets(self, player: Player) -> list[Bet]:
        amount = self._unit(player) * (2**self.loss_streak)
        return [Bet(BetType.RED, amount)]

    def record_result(self, profit: float) -> None:
        self.loss_streak = 0 if profit > 0 else self.loss_streak + 1


@dataclass
class FibonacciRedStrategy(BettingStrategy):
    name: str = "FibonacciRedStrategy"
    index: int = 0
    sequence: tuple[int, ...] = (1, 1, 2, 3, 5, 8, 13, 21, 34, 55)

    def reset(self) -> None:
        self.index = 0

    def get_bets(self, player: Player) -> list[Bet]:
        multiplier = self.sequence[min(self.index, len(self.sequence) - 1)]
        return [Bet(BetType.RED, self._unit(player) * multiplier)]

    def record_result(self, profit: float) -> None:
        if profit > 0:
            self.index = max(0, self.index - 2)
        else:
            self.index = min(self.index + 1, len(self.sequence) - 1)


STRATEGIES: dict[str, type[BettingStrategy]] = {
    "flat_red": FlatRedStrategy,
    "flat_black": FlatBlackStrategy,
    "flat_dozen": FlatDozenStrategy,
    "black_third_zero": BlackThirdZeroStrategy,
    "martingale_red": MartingaleRedStrategy,
    "fibonacci_red": FibonacciRedStrategy,
}


def create_strategy(name: str) -> BettingStrategy:
    """Build a strategy from a CLI/dashboard-friendly key."""

    try:
        return STRATEGIES[name]()
    except KeyError as exc:
        valid = ", ".join(sorted(STRATEGIES))
        raise ValueError(f"Unknown strategy '{name}'. Valid strategies: {valid}.") from exc
