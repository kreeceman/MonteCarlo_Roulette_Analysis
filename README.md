# MonteCarlo Roulette Analysis

MonteCarlo Roulette Analysis is a Python simulation toolkit for comparing roulette betting strategies across many independent sessions. It is built for analytics workflows: spin-level facts, session-level summaries, CSV exports, and a Streamlit/Plotly dashboard starter.

## Key Correction

The original prototype modeled a wheel containing both `0` and `"00"`, which is American double-zero roulette, not European single-zero roulette. This project now supports both wheel types:

- American: numbers `1-36`, `0`, and `"00"` for 38 pockets.
- European: numbers `1-36` and `0` for 37 pockets.

## Features

- Configurable starting bankroll, base unit, table limits, max spins, stop-loss, and profit target.
- Deterministic RNG seeds for reproducible Monte Carlo runs.
- Validated roulette bets and profit-only payouts.
- Built-in strategies: flat red, flat black, flat dozen, black/third dozen/zero, martingale red, and Fibonacci red.
- Spin-level and session-level pandas DataFrames.
- CSV export helpers and optional parquet export.
- Streamlit dashboard with Plotly charts.
- Pytest coverage for wheel behavior, payouts, stopping rules, simulations, and analytics.

## Architecture

```text
src/roulette_simulator/
  wheel.py          # American and European wheel metadata plus seeded spins
  bets.py           # Bet, BetType, payouts, checks, and validation
  evaluator.py      # Spin evaluation against one or more bets
  player.py         # Bankroll model
  strategies.py     # Strategy implementations
  configuration.py  # SessionConfig
  session.py        # Single-session execution and spin records
  simulation.py     # MonteCarloSimulation runner
  analytics.py      # Summary metrics and strategy comparison
  export.py         # CSV and optional parquet exports
  cli.py            # roulette-sim command
```

The legacy top-level modules are compatibility wrappers. New code should import from `roulette_simulator`.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Run Tests

```bash
pytest
```

## Run A Sample Simulation

This runs the requested sample: 1,000 simulations, 200 max spins, starting bankroll 1,000, base unit 10, American wheel, and flat red strategy.

```bash
roulette-sim --simulations 1000 --max-spins 200 --starting-bankroll 1000 --base-unit 10 --wheel-type american --strategy flat_red
```

Or run the module directly:

```bash
python -m roulette_simulator.cli
```

Outputs are written by default to:

- `outputs/spin_results.csv`
- `outputs/session_summaries.csv`

## Run The Dashboard

```bash
streamlit run dashboard.py
```

The dashboard lets you adjust wheel type, strategy, starting bankroll, base unit, table minimum, table maximum, max spins, number of simulations, stop-loss, profit target, and seed. It displays an ending bankroll histogram, sample bankroll paths, ruin and profit-target KPIs, and a strategy summary table.

## Data Dictionary

Spin-level fields:

- `simulation_id`: independent session id.
- `strategy`: strategy class name.
- `wheel_type`: `american` or `european`.
- `spin_number`: spin index within the session.
- `result`: winning pocket.
- `bankroll_before`: bankroll before wagers settle.
- `amount_wagered`: total amount placed on the spin.
- `profit`: net spin profit using profit-only payouts.
- `bankroll_after`: bankroll after the spin settles.
- `drawdown`: current drawdown from the session high bankroll.
- `stop_reason`: populated on the final recorded spin.

Session-level fields:

- `simulation_id`: independent session id.
- `strategy`: strategy class name.
- `wheel_type`: `american` or `european`.
- `starting_bankroll`: starting bankroll.
- `ending_bankroll`: final bankroll.
- `net_profit`: ending bankroll minus starting bankroll.
- `return_pct`: net profit divided by starting bankroll.
- `spins_played`: number of recorded spins.
- `max_bankroll`: highest bankroll reached.
- `min_bankroll`: lowest bankroll reached.
- `max_drawdown`: largest drawdown from a session high.
- `ruin_flag`: true when ending bankroll is below table minimum.
- `profit_target_hit`: true when the configured profit target was reached.
- `stop_reason`: final stop condition.
- `seed`: deterministic seed used for that session.

## Example Outputs

```python
from roulette_simulator.configuration import SessionConfig
from roulette_simulator.simulation import MonteCarloSimulation
from roulette_simulator.strategies import FlatRedStrategy

simulation = MonteCarloSimulation(
    strategy=FlatRedStrategy(),
    config=SessionConfig(max_spins=200, table_minimum=10, table_maximum=1000),
    starting_bankroll=1000,
    base_unit=10,
    wheel_type="american",
    number_of_simulations=1000,
    seed=42,
)
spin_df, session_df = simulation.run()
```

## Roadmap

- Add richer strategy configuration in the dashboard.
- Add combined multi-strategy comparison runs.
- Add Power BI template files that consume the exported CSVs.
- Add more table-layout bet validation edge cases around zero-adjacent bets.
- Add confidence intervals and bankroll-at-risk metrics.

## Responsible Gambling

Roulette has a negative expected value for players. This project is for simulation, analytics, and education only. It does not recommend betting systems or imply that any strategy can overcome the house edge.
