"""Export helpers for simulation data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_spin_results(spin_df: pd.DataFrame, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    spin_df.to_csv(output_path, index=False)
    return output_path


def export_session_summaries(session_df: pd.DataFrame, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    session_df.to_csv(output_path, index=False)
    return output_path


def export_parquet(df: pd.DataFrame, path: str | Path) -> Path:
    """Export to parquet when an optional parquet engine is installed."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(output_path, index=False)
    except ImportError as exc:
        raise RuntimeError("Install the 'parquet' extra to export parquet files.") from exc
    return output_path
