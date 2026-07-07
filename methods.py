from abc import ABC, abstractmethod
import bets

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