"""Betting strategies for roulette simulations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .bets import Bet, BetType
from .player import Player
from .wheel import Pocket


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


@dataclass(frozen=True)
class CustomBetLeg:
    bet_type: BetType
    units: float
    selection: Pocket | tuple[Pocket, ...] | None = None

    def __post_init__(self) -> None:
        if self.units <= 0:
            raise ValueError("Custom strategy bet units must be positive.")


@dataclass(init=False)
class CustomFlatStrategy(BettingStrategy):
    """User-defined flat strategy built from one or more bet legs."""

    legs: tuple[CustomBetLeg, ...]

    def __init__(self, legs: tuple[CustomBetLeg, ...], name: str = "Custom Strategy") -> None:
        if not legs:
            raise ValueError("Custom strategy requires at least one bet leg.")
        self.legs = legs
        self.name = name

    def get_bets(self, player: Player) -> list[Bet]:
        return [
            Bet(leg.bet_type, self._unit(player, leg.units), leg.selection)
            for leg in self.legs
        ]


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
class FlatBlackThirdZeroPatternStrategy(BettingStrategy):
    """Flat unit pattern across black, third dozen, and zero."""

    black_units: int = 2
    third_dozen_units: int = 1
    zero_units: int = 1
    name: str = "Flat 2-1-1 Black/3rd12/0"

    def get_bets(self, player: Player) -> list[Bet]:
        return [
            Bet(BetType.BLACK, self._unit(player) * self.black_units),
            Bet(BetType.DOZEN, self._unit(player) * self.third_dozen_units, 3),
            Bet(BetType.STRAIGHT, self._unit(player) * self.zero_units, 0),
        ]


@dataclass
class Flat321BlackThirdZeroStrategy(FlatBlackThirdZeroPatternStrategy):
    black_units: int = 3
    third_dozen_units: int = 2
    zero_units: int = 1
    name: str = "Flat 3-2-1 Black/3rd12/0"


@dataclass
class Flat532BlackThirdZeroStrategy(FlatBlackThirdZeroPatternStrategy):
    black_units: int = 5
    third_dozen_units: int = 3
    zero_units: int = 2
    name: str = "Flat 5-3-2 Black/3rd12/0"


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
class MartingaleBlackStrategy(BettingStrategy):
    name: str = "Martingale Black"
    loss_streak: int = 0

    def reset(self) -> None:
        self.loss_streak = 0

    def get_bets(self, player: Player) -> list[Bet]:
        return [Bet(BetType.BLACK, self._unit(player) * (2**self.loss_streak))]

    def record_result(self, profit: float) -> None:
        self.loss_streak = 0 if profit > 0 else self.loss_streak + 1


@dataclass
class ReverseMartingaleBlackStrategy(BettingStrategy):
    name: str = "Reverse Martingale Black"
    win_streak: int = 0

    def reset(self) -> None:
        self.win_streak = 0

    def get_bets(self, player: Player) -> list[Bet]:
        return [Bet(BetType.BLACK, self._unit(player) * (2**self.win_streak))]

    def record_result(self, profit: float) -> None:
        self.win_streak = self.win_streak + 1 if profit > 0 else 0


@dataclass
class OscarsGrindBlackStrategy(BettingStrategy):
    """Oscar's Grind on black, targeting one base unit per series."""

    name: str = "Oscar's Grind Black"
    units: int = 1
    series_profit: float = 0.0
    target_profit: float = 1.0

    def reset(self) -> None:
        self.units = 1
        self.series_profit = 0.0

    def get_bets(self, player: Player) -> list[Bet]:
        self.target_profit = player.base_unit
        target_remaining = max(player.base_unit - self.series_profit, player.base_unit)
        amount = min(self._unit(player, self.units), target_remaining)
        return [Bet(BetType.BLACK, amount)]

    def record_result(self, profit: float) -> None:
        self.series_profit += profit
        if self.series_profit >= self.target_profit:
            self.reset()
        elif profit > 0:
            self.units += 1


@dataclass
class DAlembertBlackStrategy(BettingStrategy):
    name: str = "D'Alembert Black"
    units: int = 1

    def reset(self) -> None:
        self.units = 1

    def get_bets(self, player: Player) -> list[Bet]:
        return [Bet(BetType.BLACK, self._unit(player, self.units))]

    def record_result(self, profit: float) -> None:
        self.units = max(1, self.units - 1) if profit > 0 else self.units + 1


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


@dataclass
class FibonacciBlackStrategy(FibonacciRedStrategy):
    name: str = "Fibonacci Black"

    def get_bets(self, player: Player) -> list[Bet]:
        multiplier = self.sequence[min(self.index, len(self.sequence) - 1)]
        return [Bet(BetType.BLACK, self._unit(player) * multiplier)]


STRATEGIES: dict[str, type[BettingStrategy]] = {
    "flat_red": FlatRedStrategy,
    "flat_black": FlatBlackStrategy,
    "flat_dozen": FlatDozenStrategy,
    "black_third_zero": BlackThirdZeroStrategy,
    "flat_2_1_1_black_third_zero": FlatBlackThirdZeroPatternStrategy,
    "flat_3_2_1_black_third_zero": Flat321BlackThirdZeroStrategy,
    "flat_5_3_2_black_third_zero": Flat532BlackThirdZeroStrategy,
    "martingale_red": MartingaleRedStrategy,
    "martingale_black": MartingaleBlackStrategy,
    "reverse_martingale_black": ReverseMartingaleBlackStrategy,
    "oscars_grind_black": OscarsGrindBlackStrategy,
    "dalembert_black": DAlembertBlackStrategy,
    "fibonacci_red": FibonacciRedStrategy,
    "fibonacci_black": FibonacciBlackStrategy,
}


def create_strategy(name: str) -> BettingStrategy:
    """Build a strategy from a CLI/dashboard-friendly key."""

    try:
        return STRATEGIES[name]()
    except KeyError as exc:
        valid = ", ".join(sorted(STRATEGIES))
        raise ValueError(f"Unknown strategy '{name}'. Valid strategies: {valid}.") from exc
