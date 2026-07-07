"""Roulette wheel definitions and spin metadata."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Literal

Pocket = int | str
WheelType = Literal["american", "european"]

RED_NUMBERS = {
    1,
    3,
    5,
    7,
    9,
    12,
    14,
    16,
    18,
    19,
    21,
    23,
    25,
    27,
    30,
    32,
    34,
    36,
}


@dataclass
class RouletteWheel:
    """Configurable roulette wheel with deterministic RNG support."""

    wheel_type: WheelType = "american"
    seed: int | None = None
    pockets: list[Pocket] = field(init=False)
    number_info: dict[Pocket, dict[str, Any]] = field(init=False)
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.wheel_type not in {"american", "european"}:
            raise ValueError("wheel_type must be 'american' or 'european'.")
        self.pockets = list(range(1, 37)) + [0]
        if self.wheel_type == "american":
            self.pockets.append("00")
        self._rng = random.Random(self.seed)
        self.number_info = self.build_number_info()
        expected = 38 if self.wheel_type == "american" else 37
        if len(self.pockets) != expected:
            raise ValueError(f"{self.wheel_type} wheel must have {expected} pockets.")

    def build_number_info(self) -> dict[Pocket, dict[str, Any]]:
        """Return per-pocket metadata for colors, outside bets, dozen, and column."""

        number_info: dict[Pocket, dict[str, Any]] = {}
        for number in range(1, 37):
            number_info[number] = {
                "color": "red" if number in RED_NUMBERS else "black",
                "dozen": ((number - 1) // 12) + 1,
                "column": ((number - 1) % 3) + 1,
                "even": number % 2 == 0,
                "odd": number % 2 == 1,
                "high": number >= 19,
                "low": number <= 18,
            }
        for green in [0, "00"]:
            if green in self.pockets:
                number_info[green] = {
                    "color": "green",
                    "dozen": None,
                    "column": None,
                    "even": False,
                    "odd": False,
                    "high": False,
                    "low": False,
                }
        return number_info

    def spin(self) -> Pocket:
        """Return one random pocket from this wheel."""

        return self._rng.choice(self.pockets)
