"""Interactive Streamlit dashboard for roulette strategy experiments."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from roulette_simulator.analytics import probability_of_busting, probability_of_doubling, strategy_comparison_summary
from roulette_simulator.bets import BetType
from roulette_simulator.configuration import SessionConfig
from roulette_simulator.simulation import MonteCarloSimulation
from roulette_simulator.strategies import STRATEGIES, BettingStrategy, CustomBetLeg, CustomFlatStrategy, create_strategy


DEFAULT_STRATEGIES = [
    "flat_black",
    "flat_2_1_1_black_third_zero",
    "flat_3_2_1_black_third_zero",
    "black_third_zero",
    "martingale_black",
    "reverse_martingale_black",
    "oscars_grind_black",
    "dalembert_black",
    "fibonacci_black",
]


def run_comparison(
    selected_strategies: tuple[str, ...],
    custom_strategy: BettingStrategy | None,
    wheel_type: str,
    starting_bankroll: float,
    base_unit: float,
    table_minimum: float,
    table_maximum: float,
    max_spins: int,
    simulations: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    spin_frames: list[pd.DataFrame] = []
    session_frames: list[pd.DataFrame] = []
    config = SessionConfig(
        max_spins=max_spins,
        stop_loss=starting_bankroll,
        profit_target=starting_bankroll,
        table_minimum=table_minimum,
        table_maximum=table_maximum,
    )
    for index, strategy_key in enumerate(selected_strategies):
        simulation = MonteCarloSimulation(
            strategy=create_strategy(strategy_key),
            config=config,
            starting_bankroll=starting_bankroll,
            base_unit=base_unit,
            wheel_type=wheel_type,
            number_of_simulations=simulations,
            seed=seed + index * 100_000,
        )
        spin_df, session_df = simulation.run()
        spin_frames.append(spin_df)
        session_frames.append(session_df)
    if custom_strategy is not None:
        simulation = MonteCarloSimulation(
            strategy=custom_strategy,
            config=config,
            starting_bankroll=starting_bankroll,
            base_unit=base_unit,
            wheel_type=wheel_type,
            number_of_simulations=simulations,
            seed=seed + 9_000_000,
        )
        spin_df, session_df = simulation.run()
        spin_frames.append(spin_df)
        session_frames.append(session_df)
    return pd.concat(spin_frames, ignore_index=True), pd.concat(session_frames, ignore_index=True)


def selection_for_bet(bet_type: BetType, index: int) -> int | str | tuple[int | str, ...] | None:
    if bet_type in {BetType.RED, BetType.BLACK, BetType.EVEN, BetType.ODD, BetType.HIGH, BetType.LOW}:
        return None
    if bet_type == BetType.DOZEN:
        return st.selectbox("Dozen", [1, 2, 3], key=f"custom_dozen_{index}")
    if bet_type == BetType.COLUMN:
        return st.selectbox("Column", [1, 2, 3], key=f"custom_column_{index}")
    if bet_type == BetType.STRAIGHT:
        value = st.text_input("Number", value="0", key=f"custom_straight_{index}")
        return "00" if value.strip() == "00" else int(value)

    expected_counts = {
        BetType.SPLIT: 2,
        BetType.STREET: 3,
        BetType.CORNER: 4,
        BetType.SIX_LINE: 6,
    }
    count = expected_counts[bet_type]
    value = st.text_input(
        "Numbers",
        value="1,2" if count == 2 else "1,2,3" if count == 3 else "1,2,4,5" if count == 4 else "1,2,3,4,5,6",
        key=f"custom_numbers_{index}",
    )
    numbers: list[int | str] = []
    for item in value.split(","):
        cleaned = item.strip()
        numbers.append("00" if cleaned == "00" else int(cleaned))
    return tuple(numbers)


st.set_page_config(page_title="Roulette Strategy Lab", layout="wide")
st.title("Roulette Strategy Lab")

with st.sidebar:
    wheel_type = st.selectbox("Wheel", ["american", "european"])
    starting_bankroll = st.number_input("Starting bankroll", min_value=10.0, value=1_000.0, step=50.0)
    base_unit = st.number_input("Base unit", min_value=1.0, value=10.0, step=1.0)
    table_minimum = st.number_input("Table minimum", min_value=1.0, value=10.0, step=1.0)
    table_maximum = st.number_input("Table maximum", min_value=table_minimum, value=1_000.0, step=50.0)
    max_spins = st.number_input("Max spins", min_value=1, value=300, step=25)
    simulations = st.number_input("Simulations per strategy", min_value=1, value=500, step=100)
    seed = st.number_input("Seed", min_value=0, value=42, step=1)
    selected_strategies = st.multiselect(
        "Strategies",
        options=sorted(STRATEGIES),
        default=[strategy for strategy in DEFAULT_STRATEGIES if strategy in STRATEGIES],
    )
    include_custom = st.toggle("Add custom strategy")
    custom_strategy: CustomFlatStrategy | None = None
    if include_custom:
        custom_name = st.text_input("Custom name", value="My Custom Strategy")
        leg_count = st.number_input("Bet legs", min_value=1, max_value=6, value=3, step=1)
        custom_legs: list[CustomBetLeg] = []
        for index in range(int(leg_count)):
            with st.expander(f"Custom bet {index + 1}", expanded=index < 3):
                bet_type = st.selectbox(
                    "Bet",
                    [
                        BetType.BLACK,
                        BetType.RED,
                        BetType.DOZEN,
                        BetType.COLUMN,
                        BetType.STRAIGHT,
                        BetType.SPLIT,
                        BetType.STREET,
                        BetType.CORNER,
                        BetType.SIX_LINE,
                        BetType.EVEN,
                        BetType.ODD,
                        BetType.HIGH,
                        BetType.LOW,
                    ],
                    format_func=lambda item: item.value.replace("_", " ").title(),
                    key=f"custom_bet_type_{index}",
                )
                units = st.number_input("Units", min_value=0.1, value=1.0, step=0.5, key=f"custom_units_{index}")
                try:
                    custom_legs.append(CustomBetLeg(bet_type, units, selection_for_bet(bet_type, index)))
                except ValueError:
                    st.error("Use valid roulette numbers for this custom bet.")
        if custom_legs:
            custom_strategy = CustomFlatStrategy(tuple(custom_legs), name=custom_name.strip() or "Custom Strategy")
    run = st.button("Run comparison", type="primary", disabled=not selected_strategies and custom_strategy is None)

if not selected_strategies and custom_strategy is None:
    st.warning("Select at least one strategy.")
elif run:
    spin_df, session_df = run_comparison(
        tuple(selected_strategies),
        custom_strategy,
        wheel_type,
        starting_bankroll,
        base_unit,
        table_minimum,
        table_maximum,
        int(max_spins),
        int(simulations),
        int(seed),
    )
    summary = strategy_comparison_summary(session_df).sort_values(
        ["chance_of_doubling", "chance_of_busting", "average_net_profit"],
        ascending=[False, True, False],
    )
    best = summary.iloc[0]

    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
    kpi_1.metric("Best strategy", best["strategy"])
    kpi_2.metric("Chance of doubling", f"{best['chance_of_doubling']:.1%}")
    kpi_3.metric("Chance of busting", f"{best['chance_of_busting']:.1%}")
    kpi_4.metric("Average profit", f"${best['average_net_profit']:,.0f}")

    display_summary = summary[
        [
            "strategy",
            "simulations",
            "average_net_profit",
            "std_net_profit",
            "chance_of_doubling",
            "chance_of_busting",
            "average_session_length",
            "average_max_drawdown",
            "worst_max_drawdown",
            "median_ending_bankroll",
        ]
    ].rename(
        columns={
            "strategy": "Strategy",
            "simulations": "Runs",
            "average_net_profit": "Average profit",
            "std_net_profit": "Std dev",
            "chance_of_doubling": "Double %",
            "chance_of_busting": "Bust %",
            "average_session_length": "Avg spins",
            "average_max_drawdown": "Avg max drawdown",
            "worst_max_drawdown": "Worst drawdown",
            "median_ending_bankroll": "Median ending bankroll",
        }
    )
    st.dataframe(
        display_summary.style.format(
            {
                "Average profit": "${:,.0f}",
                "Std dev": "${:,.0f}",
                "Double %": "{:.1%}",
                "Bust %": "{:.1%}",
                "Avg spins": "{:.1f}",
                "Avg max drawdown": "${:,.0f}",
                "Worst drawdown": "${:,.0f}",
                "Median ending bankroll": "${:,.0f}",
            }
        ),
        use_container_width=True,
    )

    chart_col, path_col = st.columns(2)
    with chart_col:
        st.plotly_chart(
            px.histogram(
                session_df,
                x="ending_bankroll",
                color="strategy",
                nbins=50,
                barmode="overlay",
                opacity=0.7,
                title="Ending bankroll distribution",
            ),
            use_container_width=True,
        )
    with path_col:
        sample_keys = session_df.groupby("strategy", group_keys=False).head(5)[["strategy", "simulation_id"]]
        sampled = spin_df.merge(sample_keys, on=["strategy", "simulation_id"], how="inner")
        st.plotly_chart(
            px.line(
                sampled,
                x="spin_number",
                y="bankroll_after",
                color="strategy",
                line_group="simulation_id",
                title="Sample bankroll paths",
            ),
            use_container_width=True,
        )

    scatter_col, box_col = st.columns(2)
    with scatter_col:
        st.plotly_chart(
            px.scatter(
                summary,
                x="chance_of_busting",
                y="chance_of_doubling",
                size="average_session_length",
                color="strategy",
                hover_data=["average_net_profit", "std_net_profit", "average_max_drawdown"],
                title="Double probability vs bust probability",
            ),
            use_container_width=True,
        )
    with box_col:
        st.plotly_chart(
            px.box(
                session_df,
                x="strategy",
                y="ending_bankroll",
                points=False,
                title="Ending bankroll spread",
            ),
            use_container_width=True,
        )

    st.download_button("Download spin results", spin_df.to_csv(index=False), "spin_results.csv", "text/csv")
    st.download_button("Download session summaries", session_df.to_csv(index=False), "session_summaries.csv", "text/csv")
else:
    st.info("Set bankroll, table limits, and strategies, then run the comparison.")
