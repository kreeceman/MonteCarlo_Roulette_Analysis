"""Analytics helpers for roulette simulation outputs."""

from __future__ import annotations

import pandas as pd


def average_ending_bankroll(session_df: pd.DataFrame) -> float:
    return float(session_df["ending_bankroll"].mean())


def median_ending_bankroll(session_df: pd.DataFrame) -> float:
    return float(session_df["ending_bankroll"].median())


def probability_of_ruin(session_df: pd.DataFrame) -> float:
    return float(session_df["ruin_flag"].mean())


def probability_of_hitting_profit_target(session_df: pd.DataFrame) -> float:
    return float(session_df["profit_target_hit"].mean())


def expected_profit_per_spin(spin_df: pd.DataFrame) -> float:
    return float(spin_df["profit"].mean())


def standard_deviation_session_profit(session_df: pd.DataFrame) -> float:
    return float(session_df["net_profit"].std(ddof=0))


def average_max_drawdown(session_df: pd.DataFrame) -> float:
    return float(session_df["max_drawdown"].mean())


def downside_percentiles(session_df: pd.DataFrame, percentiles: tuple[float, ...] = (0.01, 0.05, 0.10)) -> dict[str, float]:
    values = session_df["net_profit"].quantile(list(percentiles))
    return {f"p{int(percentile * 100)}": float(value) for percentile, value in values.items()}


def average_session_length(session_df: pd.DataFrame) -> float:
    return float(session_df["spins_played"].mean())


def strategy_comparison_summary(session_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize key risk and return metrics by strategy and wheel type."""

    grouped = session_df.groupby(["strategy", "wheel_type"], dropna=False)
    summary = grouped.agg(
        simulations=("simulation_id", "count"),
        average_ending_bankroll=("ending_bankroll", "mean"),
        median_ending_bankroll=("ending_bankroll", "median"),
        average_net_profit=("net_profit", "mean"),
        std_net_profit=("net_profit", lambda s: s.std(ddof=0)),
        probability_of_ruin=("ruin_flag", "mean"),
        probability_profit_target=("profit_target_hit", "mean"),
        average_max_drawdown=("max_drawdown", "mean"),
        average_session_length=("spins_played", "mean"),
    )
    return summary.reset_index()
