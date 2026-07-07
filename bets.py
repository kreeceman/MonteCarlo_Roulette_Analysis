from Roulette import BetType(Enum), BET_CHECKS, BET_PAYOUTS

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