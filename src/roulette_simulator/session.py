"""Single-session roulette simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .configuration import SessionConfig
from .evaluator import Evaluator
from .player import Player
from .strategies import BettingStrategy
from .wheel import RouletteWheel


@dataclass(frozen=True)
class SessionResult:
    spins: list[dict[str, Any]]
    summary: dict[str, Any]


class RouletteSession:
    """Run one roulette session for one player, wheel, and strategy."""

    def __init__(
        self,
        player: Player,
        wheel: RouletteWheel,
        strategy: BettingStrategy,
        config: SessionConfig,
        simulation_id: int = 0,
        seed: int | None = None,
    ) -> None:
        self.player = player
        self.wheel = wheel
        self.strategy = strategy
        self.config = config
        self.simulation_id = simulation_id
        self.seed = seed

    def run(self) -> SessionResult:
        self.strategy.reset()
        spin_rows: list[dict[str, Any]] = []
        max_bankroll = self.player.starting_bankroll
        min_bankroll = self.player.starting_bankroll
        max_drawdown = 0.0
        stop_reason = "max_spins"

        for spin_number in range(1, self.config.max_spins + 1):
            bankroll_before = float(self.player.bankroll or 0)
            bets = self.strategy.get_bets(self.player)
            amount_wagered = sum(bet.amount for bet in bets)
            if amount_wagered <= 0:
                stop_reason = "no_bets"
                break
            if any(bet.amount < self.config.table_minimum for bet in bets):
                stop_reason = "below_table_minimum"
                break
            if any(bet.amount > self.config.table_maximum for bet in bets):
                stop_reason = "table_maximum"
                break
            if amount_wagered > bankroll_before:
                stop_reason = "insufficient_bankroll"
                break

            spin = self.wheel.spin()
            evaluation = Evaluator.evaluate_spin(
                self.wheel,
                spin,
                bets,
                table_minimum=self.config.table_minimum,
                table_maximum=self.config.table_maximum,
            )
            self.player.apply_profit(evaluation.total_profit)
            bankroll_after = float(self.player.bankroll or 0)
            max_bankroll = max(max_bankroll, bankroll_after)
            min_bankroll = min(min_bankroll, bankroll_after)
            drawdown = max_bankroll - bankroll_after
            max_drawdown = max(max_drawdown, drawdown)
            self.strategy.record_result(evaluation.total_profit)

            row = {
                "simulation_id": self.simulation_id,
                "strategy": self.strategy.name,
                "wheel_type": self.wheel.wheel_type,
                "spin_number": spin_number,
                "result": spin,
                "bankroll_before": bankroll_before,
                "amount_wagered": amount_wagered,
                "profit": evaluation.total_profit,
                "bankroll_after": bankroll_after,
                "drawdown": drawdown,
                "stop_reason": None,
            }
            spin_rows.append(row)

            stop_reason = self._stop_reason(bankroll_after)
            if stop_reason:
                spin_rows[-1]["stop_reason"] = stop_reason
                break
            stop_reason = "max_spins"

        if spin_rows and spin_rows[-1]["stop_reason"] is None and stop_reason == "max_spins":
            spin_rows[-1]["stop_reason"] = stop_reason

        ending_bankroll = float(self.player.bankroll or 0)
        net_profit = ending_bankroll - self.player.starting_bankroll
        summary = {
            "simulation_id": self.simulation_id,
            "strategy": self.strategy.name,
            "wheel_type": self.wheel.wheel_type,
            "starting_bankroll": self.player.starting_bankroll,
            "ending_bankroll": ending_bankroll,
            "net_profit": net_profit,
            "return_pct": net_profit / self.player.starting_bankroll,
            "spins_played": len(spin_rows),
            "max_bankroll": max_bankroll,
            "min_bankroll": min_bankroll,
            "max_drawdown": max_drawdown,
            "ruin_flag": ending_bankroll < self.config.table_minimum,
            "profit_target_hit": (
                self.config.profit_target is not None and net_profit >= self.config.profit_target
            ),
            "stop_reason": stop_reason,
            "seed": self.seed,
        }
        return SessionResult(spins=spin_rows, summary=summary)

    def _stop_reason(self, bankroll_after: float) -> str | None:
        net_profit = bankroll_after - self.player.starting_bankroll
        if bankroll_after < self.config.table_minimum:
            return "ruin"
        if self.config.stop_loss is not None and net_profit <= -self.config.stop_loss:
            return "stop_loss"
        if self.config.profit_target is not None and net_profit >= self.config.profit_target:
            return "profit_target"
        return None
