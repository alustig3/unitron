from conversions import Mass

start_mode = "converter"  # set this to "timer" or "converter"
beep_num = 3  # adjust the number of beeps that occur when the countdown timer finishes

# Specify your list of ingredients
# Mass(grams_per_teaspoon, top_display_text, bottom_display_text)
ingredients = (
    Mass(4.708, "butter"),
    Mass(4.8, "baking", "poWwder"),
    Mass(3.2708, "bread", "flour"),
    Mass(2, "Cocoa"),
    Mass(4.9979, "CreaMm"),
    Mass(2.7083, "flour"),
    Mass(5.8309, "greek", "yogurt"),
    Mass(4.0417, "Mmilk"),
    Mass(4.5333, "Oil"),
    Mass(6, "salt"),
    Mass(4.167, "sugar"),
    Mass(4.9289, "Wwater"),
    Mass(4.6825, "yeast"),
)
