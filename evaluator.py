from Roulette import BET_CHECKS, BET_PAYOUTS

class Evaluator:

    @staticmethod
    def evaluate_spin(wheel, spin, bets):

        total_profit = 0

        results = []

        for bet in bets:

            check = BET_CHECKS[bet.bet_type]

            payout = BET_PAYOUTS[bet.bet_type]

            won = check(
                wheel.number_info,
                spin,
                bet
            )

            if won:

                profit = payout * bet.amount

            else:

                profit = -bet.amount

            total_profit += profit

            results.append({

                "bet": bet,
                "won": won,
                "profit": profit

            })

        return total_profit, results