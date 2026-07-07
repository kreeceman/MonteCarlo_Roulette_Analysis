"""Command line entry point for sample roulette simulations."""

from __future__ import annotations

import argparse
from pathlib import Path

from .configuration import SessionConfig
from .export import export_session_summaries, export_spin_results
from .simulation import MonteCarloSimulation
from .strategies import create_strategy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run roulette Monte Carlo simulations.")
    parser.add_argument("--simulations", type=int, default=1_000)
    parser.add_argument("--max-spins", type=int, default=200)
    parser.add_argument("--starting-bankroll", type=float, default=1_000)
    parser.add_argument("--base-unit", type=float, default=10)
    parser.add_argument("--wheel-type", choices=["american", "european"], default="american")
    parser.add_argument("--strategy", default="flat_red")
    parser.add_argument("--table-minimum", type=float, default=10)
    parser.add_argument("--table-maximum", type=float, default=1_000)
    parser.add_argument("--stop-loss", type=float, default=None)
    parser.add_argument("--profit-target", type=float, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = SessionConfig(
        max_spins=args.max_spins,
        stop_loss=args.stop_loss,
        profit_target=args.profit_target,
        table_minimum=args.table_minimum,
        table_maximum=args.table_maximum,
    )
    simulation = MonteCarloSimulation(
        strategy=create_strategy(args.strategy),
        config=config,
        starting_bankroll=args.starting_bankroll,
        base_unit=args.base_unit,
        wheel_type=args.wheel_type,
        number_of_simulations=args.simulations,
        seed=args.seed,
    )
    spin_df, session_df = simulation.run()
    spin_path = export_spin_results(spin_df, args.output_dir / "spin_results.csv")
    session_path = export_session_summaries(session_df, args.output_dir / "session_summaries.csv")
    print(f"Exported spin results to {spin_path}")
    print(f"Exported session summaries to {session_path}")
    print(session_df[["ending_bankroll", "net_profit", "stop_reason"]].describe(include="all"))


if __name__ == "__main__":
    main()
