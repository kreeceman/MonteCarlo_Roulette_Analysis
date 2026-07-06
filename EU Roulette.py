#Create the wheel
import random

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

    def spin(self):
        return random.choice(self.wheel)
#Create the properties

number_info = {}
red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
for n in range(1, 37):

    number_info[n] = {
        "color": "red" if n in red_numbers else "black",
        "dozen": ((n - 1) // 12) + 1,
        "column": ((n - 1) % 3) + 1,
        "even": n % 2 == 0,
        "high": n >= 19
    }
number_info[0] = {"color": "green"}
number_info["00"] = {"color": "green"}

# Create Bet Class
class Bet:

    def __init__(self,name,amount):

        self.name=name
        self.amount=amount

#Create Strategy Class
class Strategy:

    def get_bets(self):

        return [

            Bet("Black",2),

            Bet("Third12",1),

            Bet("Zero",1)

        ]