class Volume:
    def __init__(self, factor):
        self.factor = factor

    def to_tsp(self, input):
        return input * self.factor

    def from_tsp(self, teaspoons):
        return teaspoons / self.factor


class Mass:
    def __init__(self, factor, title, title2="        "):
        self.title = title
        self.title2 = title2
        self.factor = factor

    def from_tsp(self, teaspoons):
        return teaspoons * self.factor

    def to_tsp(self, input):
        return input / self.factor


# number of teaspoons in each volume
cup = Volume(48)  # customary cup
oz = Volume(6)
tablespoon = Volume(3)
teaspoon = Volume(1)
mL = Volume(0.202884)

ingredients = [
    Mass(4.708, "butter"),
    Mass(4.8, "baking", "pouuder"),
    Mass(3.2708, "bread", "flour"),
    Mass(2, "cocoa"),
    Mass(2.7083, "flour"),
    Mass(4.0417, "nnilk"),
    Mass(4.5333, "oil"),
    Mass(6, "salt"),
    Mass(4.167, "sugar"),
]

conversions = [cup, oz, tablespoon, teaspoon, mL, ingredients[0]]
