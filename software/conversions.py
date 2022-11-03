def normal_round(num, ndigits=0):
    if ndigits == 0:
        return int(num + 0.5)
    digit_value = 10**ndigits
    return int(num * digit_value + 0.5) / digit_value


def num_to_str(number):
    if number < 1:
        places = 4
    elif number < 10:
        places = 3
    elif number < 100:
        places = 2
    elif number < 1000:
        places = 1
    else:
        places = 0
    rounded_val = normal_round(number, places)
    if rounded_val == int(rounded_val):
        return str(int(rounded_val))
    return str(rounded_val)


class Volume:
    def __init__(self, factor):
        self.factor = factor

    def to_tsp(self, input):
        tsp = float(input) * self.factor
        return str(tsp)

    def from_tsp(self, teaspoons):
        return num_to_str(float(teaspoons) / self.factor)


class Mass:
    def __init__(self, factor, title, title2="        "):
        self.title = title
        self.title2 = title2
        self.factor = factor

    def to_tsp(self, input):
        return str(float(input) / self.factor)

    def from_tsp(self, teaspoons):
        return num_to_str(float(teaspoons) * self.factor)


# number of teaspoons in each volume
cup = Volume(48)  # customary cup
oz = Volume(6)
tablespoon = Volume(3)
teaspoon = Volume(1)
mL = Volume(0.202884)

from settings import ingredients

conversions = [cup, oz, tablespoon, teaspoon, mL, ingredients[0]]
