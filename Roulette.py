"""Deprecated compatibility module.

Use imports from ``roulette_simulator`` instead.
"""

from roulette_simulator.bets import BET_CHECKS, BET_PAYOUTS, Bet, BetType
from roulette_simulator.strategies import BlackThirdZeroStrategy as BlackThirdZeroMethod
from roulette_simulator.strategies import BettingStrategy as BetMethod
from roulette_simulator.wheel import RouletteWheel

__all__ = [
    "BET_CHECKS",
    "BET_PAYOUTS",
    "Bet",
    "BetType",
    "BetMethod",
    "BlackThirdZeroMethod",
    "RouletteWheel",
]
