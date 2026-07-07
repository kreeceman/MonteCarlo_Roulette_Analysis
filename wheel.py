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