import pandas as pd
import pytest

from roulette_simulator.analytics import probability_of_busting, probability_of_doubling, strategy_comparison_summary
from roulette_simulator.bets import Bet, BetType
from roulette_simulator.configuration import SessionConfig
from roulette_simulator.evaluator import Evaluator
from roulette_simulator.player import Player
from roulette_simulator.session import RouletteSession
from roulette_simulator.simulation import MonteCarloSimulation
from roulette_simulator.strategies import STRATEGIES, CustomBetLeg, CustomFlatStrategy, FlatRedStrategy, create_strategy
from roulette_simulator.wheel import RouletteWheel


def test_american_wheel_has_38_pockets():
    assert len(RouletteWheel("american").pockets) == 38


def test_european_wheel_has_37_pockets():
    assert len(RouletteWheel("european").pockets) == 37


def test_red_and_black_each_have_18_numbers():
    wheel = RouletteWheel("american")
    colors = [wheel.number_info[number]["color"] for number in range(1, 37)]
    assert colors.count("red") == 18
    assert colors.count("black") == 18


@pytest.mark.parametrize("spin", [0, "00"])
def test_zero_and_double_zero_lose_even_money_bets(spin):
    wheel = RouletteWheel("american")
    bets = [
        Bet(BetType.RED, 10),
        Bet(BetType.BLACK, 10),
        Bet(BetType.EVEN, 10),
        Bet(BetType.ODD, 10),
        Bet(BetType.HIGH, 10),
        Bet(BetType.LOW, 10),
    ]
    evaluation = Evaluator.evaluate_spin(wheel, spin, bets)
    assert evaluation.total_profit == -60
    assert all(not result.won for result in evaluation.bet_results)


def test_straight_up_bet_pays_35_to_1_profit():
    wheel = RouletteWheel("american")
    evaluation = Evaluator.evaluate_spin(wheel, 17, [Bet(BetType.STRAIGHT, 10, 17)])
    assert evaluation.total_profit == 350


def test_dozen_and_column_bets_pay_correctly():
    wheel = RouletteWheel("american")
    evaluation = Evaluator.evaluate_spin(
        wheel,
        34,
        [Bet(BetType.DOZEN, 10, 3), Bet(BetType.COLUMN, 10, 1)],
    )
    assert evaluation.total_profit == 40


def test_fixed_seed_produces_repeatable_spins():
    wheel_a = RouletteWheel("american", seed=123)
    wheel_b = RouletteWheel("american", seed=123)
    assert [wheel_a.spin() for _ in range(20)] == [wheel_b.spin() for _ in range(20)]


def test_bankroll_never_goes_below_zero():
    session = RouletteSession(
        Player(starting_bankroll=10, base_unit=10),
        RouletteWheel("american", seed=1),
        FlatRedStrategy(),
        SessionConfig(max_spins=20, table_minimum=10, table_maximum=100),
    )
    result = session.run()
    assert result.summary["ending_bankroll"] >= 0
    assert all(row["bankroll_after"] >= 0 for row in result.spins)


def test_stop_loss_terminates_session():
    session = RouletteSession(
        Player(starting_bankroll=100, base_unit=10),
        RouletteWheel("american", seed=1),
        FlatRedStrategy(),
        SessionConfig(max_spins=200, stop_loss=10, table_minimum=10, table_maximum=100),
    )
    result = session.run()
    assert result.summary["stop_reason"] == "stop_loss"


def test_profit_target_terminates_session():
    session = RouletteSession(
        Player(starting_bankroll=100, base_unit=10),
        RouletteWheel("american", seed=1),
        FlatRedStrategy(),
        SessionConfig(max_spins=200, profit_target=10, table_minimum=10, table_maximum=100),
    )
    result = session.run()
    assert result.summary["stop_reason"] == "profit_target"


def test_monte_carlo_returns_valid_dataframes():
    simulation = MonteCarloSimulation(
        strategy=FlatRedStrategy(),
        config=SessionConfig(max_spins=5, table_minimum=10, table_maximum=100),
        starting_bankroll=100,
        base_unit=10,
        wheel_type="american",
        number_of_simulations=3,
        seed=42,
    )
    spin_df, session_df = simulation.run()
    assert isinstance(spin_df, pd.DataFrame)
    assert isinstance(session_df, pd.DataFrame)
    assert len(session_df) == 3
    assert {
        "simulation_id",
        "strategy",
        "wheel_type",
        "spin_number",
        "result",
        "bankroll_before",
        "amount_wagered",
        "profit",
        "bankroll_after",
        "drawdown",
        "stop_reason",
    }.issubset(spin_df.columns)
    assert {
        "simulation_id",
        "strategy",
        "wheel_type",
        "starting_bankroll",
        "ending_bankroll",
        "net_profit",
        "return_pct",
        "spins_played",
        "max_bankroll",
        "min_bankroll",
        "max_drawdown",
        "ruin_flag",
        "profit_target_hit",
        "stop_reason",
        "seed",
    }.issubset(session_df.columns)


def test_strategy_comparison_analytics_return_expected_columns():
    simulation = MonteCarloSimulation(
        strategy=FlatRedStrategy(),
        config=SessionConfig(max_spins=5, table_minimum=10, table_maximum=100),
        starting_bankroll=100,
        base_unit=10,
        wheel_type="american",
        number_of_simulations=3,
        seed=42,
    )
    _, session_df = simulation.run()
    summary = strategy_comparison_summary(session_df)
    assert {
        "strategy",
        "wheel_type",
        "simulations",
        "average_ending_bankroll",
        "median_ending_bankroll",
        "average_net_profit",
        "std_net_profit",
        "probability_of_ruin",
        "probability_profit_target",
        "average_max_drawdown",
        "worst_max_drawdown",
        "chance_of_doubling",
        "chance_of_busting",
        "average_session_length",
    }.issubset(summary.columns)


def test_progression_and_flat_pattern_strategies_are_registered():
    expected = {
        "flat_2_1_1_black_third_zero",
        "flat_3_2_1_black_third_zero",
        "flat_5_3_2_black_third_zero",
        "martingale_black",
        "reverse_martingale_black",
        "oscars_grind_black",
        "dalembert_black",
        "fibonacci_black",
    }
    assert expected.issubset(STRATEGIES)
    assert all(create_strategy(name).get_bets(Player(100, 10)) for name in expected)


def test_double_and_bust_probabilities_use_session_outcomes():
    session_df = pd.DataFrame(
        [
            {
                "starting_bankroll": 100,
                "ending_bankroll": 200,
                "profit_target_hit": True,
                "stop_reason": "profit_target",
            },
            {
                "starting_bankroll": 100,
                "ending_bankroll": 0,
                "profit_target_hit": False,
                "stop_reason": "ruin",
            },
        ]
    )
    assert probability_of_doubling(session_df) == 0.5
    assert probability_of_busting(session_df) == 0.5


def test_custom_flat_strategy_builds_user_defined_bets():
    strategy = CustomFlatStrategy(
        (
            CustomBetLeg(BetType.BLACK, 2),
            CustomBetLeg(BetType.DOZEN, 1, 3),
            CustomBetLeg(BetType.STRAIGHT, 0.5, 0),
        ),
        name="Custom 2-1-half",
    )
    bets = strategy.get_bets(Player(starting_bankroll=100, base_unit=10))
    assert strategy.name == "Custom 2-1-half"
    assert [bet.amount for bet in bets] == [20, 10, 5]
    assert [bet.bet_type for bet in bets] == [BetType.BLACK, BetType.DOZEN, BetType.STRAIGHT]
