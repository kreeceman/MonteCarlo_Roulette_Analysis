# MonteCarlo Roulette Analysis

MonteCarlo Roulette Analysis is a Python simulation toolkit for comparing roulette betting strategies across many independent sessions. It is built for analytics workflows: spin-level facts, session-level summaries, CSV exports, and a Streamlit/Plotly dashboard starter.

## How to use

This project is easiest to use through the web dashboard.

### 1. Open PowerShell

Open PowerShell on your computer.

### 2. Go to the project folder

If you already downloaded or cloned the project, go into that folder:

```powershell
cd path\to\MonteCarlo_Roulette_Analysis
```

For example, if you cloned it into your current folder:

```powershell
cd MonteCarlo_Roulette_Analysis
```

If you do not have the project yet, clone it first:

```powershell
git clone https://github.com/kreeceman/MonteCarlo_Roulette_Analysis.git
cd MonteCarlo_Roulette_Analysis
```

### 3. Install the app

Copy and paste these commands:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
```

You only need to do this install step the first time.

### 4. Start the dashboard

Copy and paste this command:

```powershell
.venv\Scripts\python -m streamlit run dashboard.py
```

### 5. Open it in your browser

PowerShell will print a local website link. It usually looks like this:

```text
http://localhost:8501
```

Open that link in your browser.

### 6. Run a strategy comparison

In the dashboard:

1. Set `Starting bankroll`.
2. Set `Base unit`.
3. Pick one or more strategies.
4. Optional: turn on `Add custom strategy` to create your own betting mix.
5. Click `Run comparison`.

The dashboard will show:

- which strategy performed best
- chance of doubling your bankroll
- chance of busting
- average profit
- ending bankroll charts
- sample bankroll paths
- CSV download buttons

### 7. Stop the dashboard

When you are done, go back to PowerShell and press:

```text
Ctrl + C
```

## Key Correction

The original prototype modeled a wheel containing both `0` and `"00"`, which is American double-zero roulette, not European single-zero roulette. This project now supports both wheel types:

- American: numbers `1-36`, `0`, and `"00"` for 38 pockets.
- European: numbers `1-36` and `0` for 37 pockets.

## Features

- Configurable starting bankroll, base unit, table limits, max spins, stop-loss, and profit target.
- Deterministic RNG seeds for reproducible Monte Carlo runs.
- Validated roulette bets and profit-only payouts.
- Built-in strategies: flat red/black/dozen, 2-1-1/3-2-1/5-3-2 black-third-dozen-zero patterns, black/third dozen/zero, martingale, reverse martingale, Oscar's Grind, D'Alembert, and Fibonacci.
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

## Setup Only

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Run Tests

```bash
.venv\Scripts\python -m pytest
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

```powershell
.venv\Scripts\python -m streamlit run dashboard.py
```

The dashboard lets you compare multiple strategies at once while adjusting wheel type, starting bankroll, base unit, table minimum, table maximum, max spins, simulations per strategy, and seed. It also includes a custom strategy builder where you can add one or more flat bet legs, choose bet type, units, and selections, then compare that custom strategy against the built-ins. It uses a double-or-bust frame by default: the profit target is one starting bankroll, and the stop-loss is one starting bankroll.

It displays average profit, standard deviation, chance of doubling, chance of busting, average session length, maximum drawdown, ending bankroll distributions, sample bankroll paths, and downloadable spin/session CSVs.

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
- Add more table-layout bet validation edge cases around zero-adjacent bets.
- Add confidence intervals and bankroll-at-risk metrics.

## Responsible Gambling

Roulette has a negative expected value for players. This project is for simulation, analytics, and education only. It does not recommend betting systems or imply that any strategy can overcome the house edge.
