#Create the wheel
import random
from enum import Enum

class RouletteWheel:

    def __init__(self):

        self.wheel = [
            1,2,3,4,5,6,
            7,8,9,10,11,12,
            13,14,15,16,17,18,
            19,20,21,22,23,24,
            25,26,27,28,29,30,
            31,32,33,34,35,36,
            0,"00"
        ]
        self.number_info = self.build_number_info()
    def build_number_info(self):

        number_info = {}

        RED_NUMBERS = {
        1,3,5,7,9,
        12,14,16,18,
        19,21,23,25,
        27,30,32,34,36
    }

        for n in range(1, 37):

            number_info[n] = {

                "color": "red" if n in RED_NUMBERS else "black",
                "dozen": ((n - 1) // 12) + 1,
                "column": ((n - 1) % 3) + 1,
                "even": n % 2 == 0,
                "odd": n % 2 == 1,
                "high": n >= 19,
                "low": n <= 18

            }

        number_info[0] = {
            "color": "green",
            "dozen": None,
            "column": None,
            "even": False,
            "odd": False,
            "high": False,
            "low": False
    }

        number_info["00"] = {
            "color": "green",
            "dozen": None,
            "column": None,
            "even": False,
            "odd": False,
            "high": False,
            "low": False
    }

        return number_info

    def spin(self):
        return random.choice(self.wheel)
#Create the properties

# Create Bet Class
class Bet:

    def __repr__(self):
        return (
            f"Bet("
            f"{self.bet_type.name}, "
            f"amount={self.amount}, "
            f"selection={self.selection})"
        )

    def __init__(self,bet_type,amount, selection=None):

        self.bet_type= bet_type
        self.amount=amount
        self.selection = selection
    

class BetType(Enum):
    BLACK = "Black"
    RED = "Red"
    DOZEN = "Dozen"
    COLUMN = "Column"
    STRAIGHT = "Straight"
    SPLIT = "Split"
    STREET = "Street"
    CORNER = "Corner"
    SIX_LINE = "SixLine"
    EVEN = "Even"
    ODD = "Odd"
    HIGH = "High"
    LOW = "Low"

#Create BetMethod Class
from abc import ABC, abstractmethod

class BetMethod(ABC):

    @abstractmethod
    def get_bets(self, player):
        pass

class BlackThirdZeroMethod(BetMethod):

    def get_bets(self, player):

        return [

            Bet(BetType.BLACK, 2),

            Bet(BetType.DOZEN, 1, 3),

            Bet(BetType.STRAIGHT, 1, (0,))

        ]
        
BET_PAYOUTS = {

    BetType.BLACK:1,
    BetType.RED:1,
    BetType.EVEN:1,
    BetType.ODD:1,
    BetType.HIGH:1,
    BetType.LOW:1,
    BetType.COLUMN:2,
    BetType.DOZEN:2,
    BetType.STRAIGHT:35,
    BetType.SPLIT:17,
    BetType.STREET:11,
    BetType.CORNER:8,
    BetType.SIX_LINE:5

}

BET_CHECKS = {

    BetType.BLACK:lambda info, spin, bet: info[spin]["color"] == "black",
    BetType.RED:lambda info, spin, bet: info[spin]["color"] == "red",
    BetType.EVEN:lambda info, spin, bet: spin not in (0,"00") and info[spin]["even"],
    BetType.ODD:lambda info, spin, bet: spin not in (0,"00") and info[spin]["odd"],
    BetType.HIGH:lambda info, spin, bet: spin not in (0,"00") and info[spin]["high"],
    BetType.LOW:lambda info, spin, bet: spin not in (0,"00") and info[spin]["low"],
    BetType.COLUMN:lambda info, spin, bet: spin not in (0,"00") and info[spin]["column"] == bet.selection,
    BetType.DOZEN:lambda info, spin, bet: spin not in (0,"00") and info[spin]["dozen"] == bet.selection,
    BetType.STRAIGHT:lambda info, spin, bet: spin in bet.selection,
    BetType.SPLIT:lambda info, spin, bet: spin in bet.selection,
    BetType.STREET:lambda info, spin, bet: spin in bet.selection,
    BetType.CORNER:lambda info, spin, bet: spin in bet.selection,
    BetType.SIX_LINE:lambda info, spin, bet: spin in bet.selection

}