# Power BI Dashboard Guide

Use the simulator as the data engine and Power BI as the visualization layer.

## Generate Data

```powershell
python -m roulette_simulator.powerbi --output-dir powerbi_exports --simulations 1000 --max-spins 300 --starting-bankroll 1000 --base-unit 10
```

This creates:

- `powerbi_exports/spin_results.csv`
- `powerbi_exports/session_summaries.csv`
- `powerbi_exports/strategy_summary.csv`
- `powerbi_exports/data_dictionary.csv`

## Load Into Power BI Desktop

1. Open Power BI Desktop.
2. Choose **Get Data > Text/CSV**.
3. Import all four CSV files from `powerbi_exports`.
4. In Model view, relate:
   - `strategy_summary[strategy]` to `session_summaries[strategy]`
   - `session_summaries[simulation_id]` to `spin_results[simulation_id]`

If you compare the same simulation ids across many strategies, use a composite key column in Power Query:

```text
strategy_simulation_id = [strategy] & "-" & Text.From([simulation_id])
```

Create it in both `session_summaries` and `spin_results`, then relate on that key.

## Suggested Measures

```DAX
Average Profit = AVERAGE(session_summaries[net_profit])
Profit Std Dev = STDEV.P(session_summaries[net_profit])
Chance of Doubling = AVERAGE(strategy_summary[chance_of_doubling])
Chance of Busting = AVERAGE(strategy_summary[chance_of_busting])
Average Session Length = AVERAGE(session_summaries[spins_played])
Average Max Drawdown = AVERAGE(session_summaries[max_drawdown])
Worst Drawdown = MAX(session_summaries[max_drawdown])
```

## Recommended Pages

### Strategy Comparison

- Table or matrix from `strategy_summary`
- KPI cards for best chance of doubling, lowest bust rate, and average profit
- Bar chart of `chance_of_doubling` by strategy
- Bar chart of `chance_of_busting` by strategy

### Risk / Reward Matrix

- Scatter plot
- X-axis: `chance_of_busting`
- Y-axis: `chance_of_doubling`
- Size: `average_session_length`
- Legend: `strategy`

### Ending Bankroll Distribution

- Histogram using `session_summaries[ending_bankroll]`
- Legend by `strategy`
- Box plot custom visual if available

### Bankroll Paths

- Line chart from `spin_results`
- X-axis: `spin_number`
- Y-axis: `bankroll_after`
- Legend: `strategy`
- Filter to a small set of `simulation_id` values for readability

## Refresh Workflow

Rerun the export command, then click **Refresh** in Power BI Desktop. Keep the export folder path stable so Power BI can reuse the same source definitions.
