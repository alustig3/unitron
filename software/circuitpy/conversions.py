class Unit:
    def __init__(self, factor):
        self.factor = factor

    def to_tsp(self, input):
        return input * self.factor

    def from_tsp(self, teaspoons):
        return teaspoons / self.factor

class Ingredient:
    def __init__(self, factor, title, title2="        "):
        self.title = title
        self.title2 = title2
        self.factor = factor

    def from_tsp(self, teaspoons):
        return teaspoons * self.factor

    def to_tsp(self, input):
        return input / self.factor

butter = Ingredient(4.708, "butter")
baking_powder = Ingredient(4.8, "baking", "pouuder")
bread_flour = Ingredient(3.2708, "bread", "flour")
cocoa = Ingredient(2, "cocoa")
flour = Ingredient(2.7083, "flour")
milk = Ingredient(4.0417, "nnilk")
oil = Ingredient(4.5333, "oil")
salt = Ingredient(6, "salt")
sugar = Ingredient(4.167, "sugar")

ingredients = [baking_powder, bread_flour, butter, cocoa, flour, milk, oil, salt, sugar]

cup_tsp = Unit(48)  # customary cup
tbsp_tsp = Unit(3)
tsp_tsp = Unit(1)
oz_tsp = Unit(6)
ml_tsp = Unit(0.202884)
conversions = [cup_tsp, tbsp_tsp, tsp_tsp, oz_tsp, ml_tsp, ingredients[0]]