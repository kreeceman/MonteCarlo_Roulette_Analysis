"""Streamlit dashboard starter for roulette Monte Carlo analysis."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from roulette_simulator.analytics import probability_of_hitting_profit_target, probability_of_ruin, strategy_comparison_summary
from roulette_simulator.configuration import SessionConfig
from roulette_simulator.simulation import MonteCarloSimulation
from roulette_simulator.strategies import STRATEGIES, create_strategy


st.set_page_config(page_title="Roulette Monte Carlo", layout="wide")
st.title("Roulette Monte Carlo Dashboard")

with st.sidebar:
    wheel_type = st.selectbox("Wheel type", ["american", "european"])
    strategy_name = st.selectbox("Strategy", sorted(STRATEGIES))
    starting_bankroll = st.number_input("Starting bankroll", min_value=1.0, value=1_000.0, step=50.0)
    base_unit = st.number_input("Base unit", min_value=1.0, value=10.0, step=1.0)
    table_minimum = st.number_input("Table minimum", min_value=1.0, value=10.0, step=1.0)
    table_maximum = st.number_input("Table maximum", min_value=table_minimum, value=1_000.0, step=50.0)
    max_spins = st.number_input("Max spins", min_value=1, value=200, step=10)
    simulations = st.number_input("Number of simulations", min_value=1, value=500, step=100)
    stop_loss = st.number_input("Stop-loss", min_value=0.0, value=0.0, step=50.0)
    profit_target = st.number_input("Profit target", min_value=0.0, value=0.0, step=50.0)
    seed = st.number_input("Seed", min_value=0, value=42, step=1)
    run = st.button("Run simulation", type="primary")

if run:
    config = SessionConfig(
        max_spins=int(max_spins),
        stop_loss=stop_loss or None,
        profit_target=profit_target or None,
        table_minimum=table_minimum,
        table_maximum=table_maximum,
    )
    simulation = MonteCarloSimulation(
        strategy=create_strategy(strategy_name),
        config=config,
        starting_bankroll=starting_bankroll,
        base_unit=base_unit,
        wheel_type=wheel_type,
        number_of_simulations=int(simulations),
        seed=int(seed),
    )
    spin_df, session_df = simulation.run()
    kpi_ruin, kpi_target = st.columns(2)
    kpi_ruin.metric("Probability of ruin", f"{probability_of_ruin(session_df):.1%}")
    kpi_target.metric("Profit target hit", f"{probability_of_hitting_profit_target(session_df):.1%}")

    chart_col, path_col = st.columns(2)
    with chart_col:
        st.plotly_chart(
            px.histogram(session_df, x="ending_bankroll", nbins=40, title="Ending bankroll distribution"),
            use_container_width=True,
        )
    with path_col:
        sample_ids = session_df["simulation_id"].head(10).tolist()
        sample_paths = spin_df[spin_df["simulation_id"].isin(sample_ids)]
        st.plotly_chart(
            px.line(
                sample_paths,
                x="spin_number",
                y="bankroll_after",
                color="simulation_id",
                title="Sample bankroll paths",
            ),
            use_container_width=True,
        )

    st.dataframe(strategy_comparison_summary(session_df), use_container_width=True)
    st.download_button("Download spin results", spin_df.to_csv(index=False), "spin_results.csv", "text/csv")
    st.download_button("Download session summaries", session_df.to_csv(index=False), "session_summaries.csv", "text/csv")
else:
    st.info("Choose parameters in the sidebar and run a simulation.")
