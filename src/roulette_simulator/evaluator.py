"""Roulette bet evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from .bets import BET_PAYOUTS, Bet, bet_wins, validate_bet
from .wheel import Pocket, RouletteWheel


@dataclass(frozen=True)
class BetResult:
    bet: Bet
    won: bool
    profit: float


@dataclass(frozen=True)
class SpinEvaluation:
    total_profit: float
    bet_results: list[BetResult]


class Evaluator:
    """Evaluate one spin against one or more bets."""

    @staticmethod
    def evaluate_spin(
        wheel: RouletteWheel,
        spin: Pocket,
        bets: list[Bet],
        table_minimum: float | None = None,
        table_maximum: float | None = None,
    ) -> SpinEvaluation:
        total_profit = 0.0
        results: list[BetResult] = []
        for bet in bets:
            validate_bet(bet, wheel, table_minimum, table_maximum)
            won = bet_wins(bet, wheel, spin)
            profit = bet.amount * BET_PAYOUTS[bet.bet_type] if won else -bet.amount
            total_profit += profit
            results.append(BetResult(bet=bet, won=won, profit=profit))
        return SpinEvaluation(total_profit=total_profit, bet_results=results)
