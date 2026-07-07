"""Bet models, payouts, and validation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .wheel import Pocket, RouletteWheel


class BetType(Enum):
    BLACK = "black"
    RED = "red"
    DOZEN = "dozen"
    COLUMN = "column"
    STRAIGHT = "straight"
    SPLIT = "split"
    STREET = "street"
    CORNER = "corner"
    SIX_LINE = "six_line"
    EVEN = "even"
    ODD = "odd"
    HIGH = "high"
    LOW = "low"


BET_PAYOUTS: dict[BetType, int] = {
    BetType.BLACK: 1,
    BetType.RED: 1,
    BetType.EVEN: 1,
    BetType.ODD: 1,
    BetType.HIGH: 1,
    BetType.LOW: 1,
    BetType.COLUMN: 2,
    BetType.DOZEN: 2,
    BetType.STRAIGHT: 35,
    BetType.SPLIT: 17,
    BetType.STREET: 11,
    BetType.CORNER: 8,
    BetType.SIX_LINE: 5,
}


@dataclass(frozen=True)
class Bet:
    """A single roulette wager."""

    bet_type: BetType
    amount: float
    selection: Pocket | tuple[Pocket, ...] | None = None

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("Bet amount must be positive.")


def normalize_selection(selection: Pocket | tuple[Pocket, ...] | None) -> tuple[Pocket, ...]:
    if selection is None:
        return ()
    if isinstance(selection, tuple):
        return selection
    return (selection,)


def validate_bet(
    bet: Bet,
    wheel: RouletteWheel,
    table_minimum: float | None = None,
    table_maximum: float | None = None,
) -> None:
    """Validate amount, table limits, selection cardinality, and legal pockets."""

    if table_minimum is not None and bet.amount < table_minimum:
        raise ValueError(f"Bet amount {bet.amount} is below table minimum {table_minimum}.")
    if table_maximum is not None and bet.amount > table_maximum:
        raise ValueError(f"Bet amount {bet.amount} exceeds table maximum {table_maximum}.")

    selection = normalize_selection(bet.selection)
    valid_pockets = set(wheel.pockets)
    if any(pocket not in valid_pockets for pocket in selection):
        raise ValueError(f"Bet selection {selection} contains pockets not on the wheel.")

    if bet.bet_type in {BetType.RED, BetType.BLACK, BetType.EVEN, BetType.ODD, BetType.HIGH, BetType.LOW}:
        if selection:
            raise ValueError(f"{bet.bet_type.value} bets do not take a selection.")
        return
    if bet.bet_type in {BetType.DOZEN, BetType.COLUMN}:
        if bet.selection not in {1, 2, 3}:
            raise ValueError(f"{bet.bet_type.value} selection must be 1, 2, or 3.")
        return

    expected_counts = {
        BetType.STRAIGHT: 1,
        BetType.SPLIT: 2,
        BetType.STREET: 3,
        BetType.CORNER: 4,
        BetType.SIX_LINE: 6,
    }
    expected = expected_counts[bet.bet_type]
    if len(selection) != expected:
        raise ValueError(f"{bet.bet_type.value} bet requires {expected} selected pocket(s).")
    if len(set(selection)) != len(selection):
        raise ValueError("Bet selection cannot contain duplicates.")
    if any(pocket == "00" for pocket in selection) and bet.bet_type != BetType.STRAIGHT:
        raise ValueError("'00' is only supported for straight-up bets.")

    numeric = [pocket for pocket in selection if isinstance(pocket, int)]
    if bet.bet_type != BetType.STRAIGHT and 0 in numeric:
        raise ValueError("0 is only supported for straight-up bets.")
    if bet.bet_type == BetType.SPLIT and not _is_valid_split(numeric):
        raise ValueError("Split selection must be two adjacent layout numbers.")
    if bet.bet_type == BetType.STREET and not _is_valid_street(numeric):
        raise ValueError("Street selection must be one horizontal row of three numbers.")
    if bet.bet_type == BetType.CORNER and not _is_valid_corner(numeric):
        raise ValueError("Corner selection must be four numbers forming a 2x2 block.")
    if bet.bet_type == BetType.SIX_LINE and not _is_valid_six_line(numeric):
        raise ValueError("Six-line selection must be two adjacent rows of three numbers.")


def bet_wins(bet: Bet, wheel: RouletteWheel, spin: Pocket) -> bool:
    """Return whether a bet wins for a spin."""

    check = BET_CHECKS[bet.bet_type]
    return check(wheel, spin, bet)


def _is_valid_split(numbers: list[int]) -> bool:
    a, b = sorted(numbers)
    same_row = (a - 1) // 3 == (b - 1) // 3 and b - a == 1
    same_column = b - a == 3
    return same_row or same_column


def _is_valid_street(numbers: list[int]) -> bool:
    ordered = sorted(numbers)
    return len(ordered) == 3 and ordered[1] == ordered[0] + 1 and ordered[2] == ordered[0] + 2 and ordered[0] % 3 == 1


def _is_valid_corner(numbers: list[int]) -> bool:
    ordered = sorted(numbers)
    low = ordered[0]
    return ordered == [low, low + 1, low + 3, low + 4] and low % 3 in {1, 2}


def _is_valid_six_line(numbers: list[int]) -> bool:
    ordered = sorted(numbers)
    low = ordered[0]
    return ordered == list(range(low, low + 6)) and low % 3 == 1


BetCheck = Callable[[RouletteWheel, Pocket, Bet], bool]
BET_CHECKS: dict[BetType, BetCheck] = {
    BetType.BLACK: lambda wheel, spin, bet: wheel.number_info[spin]["color"] == "black",
    BetType.RED: lambda wheel, spin, bet: wheel.number_info[spin]["color"] == "red",
    BetType.EVEN: lambda wheel, spin, bet: spin not in (0, "00") and wheel.number_info[spin]["even"],
    BetType.ODD: lambda wheel, spin, bet: spin not in (0, "00") and wheel.number_info[spin]["odd"],
    BetType.HIGH: lambda wheel, spin, bet: spin not in (0, "00") and wheel.number_info[spin]["high"],
    BetType.LOW: lambda wheel, spin, bet: spin not in (0, "00") and wheel.number_info[spin]["low"],
    BetType.COLUMN: lambda wheel, spin, bet: spin not in (0, "00") and wheel.number_info[spin]["column"] == bet.selection,
    BetType.DOZEN: lambda wheel, spin, bet: spin not in (0, "00") and wheel.number_info[spin]["dozen"] == bet.selection,
    BetType.STRAIGHT: lambda wheel, spin, bet: spin in normalize_selection(bet.selection),
    BetType.SPLIT: lambda wheel, spin, bet: spin in normalize_selection(bet.selection),
    BetType.STREET: lambda wheel, spin, bet: spin in normalize_selection(bet.selection),
    BetType.CORNER: lambda wheel, spin, bet: spin in normalize_selection(bet.selection),
    BetType.SIX_LINE: lambda wheel, spin, bet: spin in normalize_selection(bet.selection),
}
