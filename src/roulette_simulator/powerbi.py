"""Power BI-ready export workflow for roulette simulations."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .analytics import strategy_comparison_summary
from .configuration import SessionConfig
from .simulation import MonteCarloSimulation
from .strategies import STRATEGIES, create_strategy


POWER_BI_FIELDS = [
    ("spin_results", "simulation_id", "Independent simulation/session id."),
    ("spin_results", "strategy", "Betting strategy name."),
    ("spin_results", "wheel_type", "Roulette wheel variant."),
    ("spin_results", "spin_number", "Spin index within a session."),
    ("spin_results", "result", "Winning roulette pocket."),
    ("spin_results", "bankroll_before", "Bankroll before the spin settles."),
    ("spin_results", "amount_wagered", "Total amount wagered on the spin."),
    ("spin_results", "profit", "Net profit from the spin."),
    ("spin_results", "bankroll_after", "Bankroll after the spin settles."),
    ("spin_results", "drawdown", "Drawdown from the session high after this spin."),
    ("spin_results", "stop_reason", "Final stop reason when populated."),
    ("session_summaries", "simulation_id", "Independent simulation/session id."),
    ("session_summaries", "strategy", "Betting strategy name."),
    ("session_summaries", "wheel_type", "Roulette wheel variant."),
    ("session_summaries", "starting_bankroll", "Initial bankroll."),
    ("session_summaries", "ending_bankroll", "Final bankroll."),
    ("session_summaries", "net_profit", "Ending bankroll minus starting bankroll."),
    ("session_summaries", "return_pct", "Net profit divided by starting bankroll."),
    ("session_summaries", "spins_played", "Number of spins played."),
    ("session_summaries", "max_bankroll", "Highest bankroll reached."),
    ("session_summaries", "min_bankroll", "Lowest bankroll reached."),
    ("session_summaries", "max_drawdown", "Largest session drawdown."),
    ("session_summaries", "ruin_flag", "Whether the session ended below table minimum."),
    ("session_summaries", "profit_target_hit", "Whether the double-bankroll target was hit."),
    ("session_summaries", "stop_reason", "Final stop condition."),
    ("session_summaries", "seed", "Seed used for the session."),
    ("strategy_summary", "chance_of_doubling", "Share of sessions that hit the profit target."),
    ("strategy_summary", "chance_of_busting", "Share of sessions ending in ruin, stop-loss, or insufficient bankroll."),
    ("strategy_summary", "average_max_drawdown", "Average maximum drawdown by strategy."),
]


def run_powerbi_export(
    output_dir: str | Path,
    strategies: list[str],
    wheel_type: str = "american",
    simulations: int = 1_000,
    max_spins: int = 300,
    starting_bankroll: float = 1_000,
    base_unit: float = 10,
    table_minimum: float = 10,
    table_maximum: float = 1_000,
    seed: int = 42,
) -> dict[str, Path]:
    """Run strategy simulations and export Power BI-ready CSV tables."""

    export_dir = Path(output_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    config = SessionConfig(
        max_spins=max_spins,
        stop_loss=starting_bankroll,
        profit_target=starting_bankroll,
        table_minimum=table_minimum,
        table_maximum=table_maximum,
    )
    spin_frames: list[pd.DataFrame] = []
    session_frames: list[pd.DataFrame] = []
    for index, strategy_name in enumerate(strategies):
        simulation = MonteCarloSimulation(
            strategy=create_strategy(strategy_name),
            config=config,
            starting_bankroll=starting_bankroll,
            base_unit=base_unit,
            wheel_type=wheel_type,  # type: ignore[arg-type]
            number_of_simulations=simulations,
            seed=seed + index * 100_000,
        )
        spin_df, session_df = simulation.run()
        spin_frames.append(spin_df)
        session_frames.append(session_df)

    spin_results = pd.concat(spin_frames, ignore_index=True)
    session_summaries = pd.concat(session_frames, ignore_index=True)
    strategy_summary = strategy_comparison_summary(session_summaries)
    data_dictionary = pd.DataFrame(POWER_BI_FIELDS, columns=["table", "field", "description"])

    outputs = {
        "spin_results": export_dir / "spin_results.csv",
        "session_summaries": export_dir / "session_summaries.csv",
        "strategy_summary": export_dir / "strategy_summary.csv",
        "data_dictionary": export_dir / "data_dictionary.csv",
    }
    spin_results.to_csv(outputs["spin_results"], index=False)
    session_summaries.to_csv(outputs["session_summaries"], index=False)
    strategy_summary.to_csv(outputs["strategy_summary"], index=False)
    data_dictionary.to_csv(outputs["data_dictionary"], index=False)
    return outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export roulette simulation data for Power BI.")
    parser.add_argument("--output-dir", type=Path, default=Path("powerbi_exports"))
    parser.add_argument("--strategies", nargs="+", default=sorted(STRATEGIES))
    parser.add_argument("--wheel-type", choices=["american", "european"], default="american")
    parser.add_argument("--simulations", type=int, default=1_000)
    parser.add_argument("--max-spins", type=int, default=300)
    parser.add_argument("--starting-bankroll", type=float, default=1_000)
    parser.add_argument("--base-unit", type=float, default=10)
    parser.add_argument("--table-minimum", type=float, default=10)
    parser.add_argument("--table-maximum", type=float, default=1_000)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    outputs = run_powerbi_export(
        output_dir=args.output_dir,
        strategies=args.strategies,
        wheel_type=args.wheel_type,
        simulations=args.simulations,
        max_spins=args.max_spins,
        starting_bankroll=args.starting_bankroll,
        base_unit=args.base_unit,
        table_minimum=args.table_minimum,
        table_maximum=args.table_maximum,
        seed=args.seed,
    )
    for table, path in outputs.items():
        print(f"Exported {table} to {path}")


if __name__ == "__main__":
    main()
