# https://wiki.seeedstudio.com/XIAO_BLE/
# https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/usage
import time

startup = time.monotonic()
import asyncio
import board
import as1115 as driver
import neopixel
import busio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_bus_device.i2c_device import I2CDevice

pixel_pin = board.D8
num_pixels = 10
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1)
RED_dim = (64, 0, 0)
YELLOW_dim = (64, 27, 0)
RED = (128, 0, 0)
YELLOW = (128, 54, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 128)
pixels.fill(BLACK)
pixels.show()
fractions = (1, 0.1, 0.01, 0.001, 0.0001, 0.00001)

pwr_btn = DigitalInOut(board.D6)
pwr_btn.direction = Direction.INPUT
pwr_btn.pull = Pull.UP

keypress = DigitalInOut(board.D1)
keypress.direction = Direction.INPUT
keypress.pull = Pull.UP

toggle = DigitalInOut(board.D7)
toggle.direction = Direction.INPUT
toggle.pull = Pull.UP

display_brightness = 9  # 0-15
numDigits = 8
i2cbus = busio.I2C(board.SCL, board.SDA)

try:
    i2c_device = I2CDevice(i2cbus, 0)
    with i2c_device as bus_device:
        bus_device.write(bytes([driver.SHUTDOWN, 0x01]))
        bus_device.write(bytes([driver.DECODE, 0x00]))
        bus_device.write(bytes([driver.KEYSCAN, numDigits - 1]))
        bus_device.write(bytes([driver.INTENSITY, display_brightness]))
        bus_device.write(bytes([0x2D, 0x01]))  # set self addressing mode
    print("fresh start up with address 0")
except ValueError:
    print("already self-addressing")
top_disp = driver.SegmentDisplay(1, i2cbus)
bottom_disp = driver.SegmentDisplay(3, i2cbus)

top_disp.wake()
bottom_disp.wake()

time_to_display = time.monotonic()
print("monotonic", time_to_display)
print("startup time", time_to_display - startup)


class Ingredient:
    def __init__(self, factor, title, title2="        "):
        self.title = title
        self.title2 = title2
        self.factor = factor
        self.decimals = 4

    def from_tsp(self, teaspoons):
        return teaspoons * self.factor


class Linear:
    def __init__(self, factor, decimals):
        self.factor = factor
        self.decimals = decimals

    def to_tsp(self, input):
        return input * self.factor

    def from_tsp(self, teaspoons):
        return teaspoons / self.factor


class Shared:
    def __init__(self, top_disp, btm_disp, power_button):
        self.toggle_up = True
        self.input = 0
        self.output = 0
        self.top_disp = top_disp
        self.btm_disp = btm_disp
        self.blink_disp = top_disp
        cup_tsp = Linear(48, 4)  # customary cup
        tbsp_tsp = Linear(3, 4)
        tsp_tsp = Linear(1, 4)
        oz_tsp = Linear(6, 4)
        ml_tsp = Linear(0.202884, 4)
        self.conversions = [cup_tsp, tbsp_tsp, tsp_tsp, oz_tsp, ml_tsp]
        self.top_index = 0
        self.bottom_index = 0
        self.top_unit = self.conversions[0]
        self.bottom_unit = self.conversions[0]

        flour = Ingredient(2.7083, "flour")
        sugar = Ingredient(4.167, "sugar")
        butter = Ingredient(4.708, "butter")
        cocoa = Ingredient(2, "cocoa")
        baking_powder = Ingredient(4.8, "baking", "pouuder")
        bread_flour = Ingredient(3.2708, "bread", "flour")
        milk = Ingredient(4.0417, "nnilk")
        oil = Ingredient(4.5333, "oil")
        salt = Ingredient(6, "salt")
        self.ingredients = [flour, sugar, butter, cocoa, baking_powder, bread_flour, milk, oil, salt]
        self.ingredient = self.ingredients[0]

        self.converter = self.conversions[0]
        self.mode = 0
        self.dot_added = False
        self.decimal_place = 0
        self.pwr_btn = power_button
        pixels[9 - 2 * self.mode - 1] = RED
        pixels[9 - 2 * self.mode] = RED
        self.count = 0
        self.negative_input = False
        self.skip_rebound = False


    def update_displays(self):
        if self.toggle_up:
            self.top_disp.display(self.input, self.converter.decimals, self.dot_added)
            output = self.ingredient.from_tsp(self.converter.to_tsp(self.input))
            self.btm_disp.display(output, 3, self.dot_added)
        else:
            self.top_disp.display(self.input, self.converter.decimals, self.dot_added)
            output = self.bottom_unit.from_tsp(self.top_unit.to_tsp(self.input))
            self.btm_disp.display(output, 3, self.dot_added)

    def next_volume(self, direction=1):
        pixels[9 - 2 * self.mode] = BLACK
        pixels[9 - 2 * self.mode - 1] = BLACK
        self.mode += direction
        if direction > 0:
            if self.mode == len(self.conversions):
                self.mode = 0
        else:
            if self.mode == -1:
                self.mode = len(self.conversions) - 1

        self.converter = self.conversions[self.mode]
        pixels[9 - 2 * self.mode - 1] = RED
        pixels[9 - 2 * self.mode] = RED
        # pixels[9 - 2 * self.mode] = YELLOW


    def top_next(self, direction=1):
        pixels[9 - 2 * self.top_index - 1] = BLACK
        self.top_index += direction
        if direction > 0:
            if self.top_index == len(self.conversions):
                self.top_index = 0
        else:
            if self.top_index == -1:
                self.top_index = len(self.conversions) - 1

        pixels[9 - 2 * self.top_index - 1] = RED
        self.top_unit = self.conversions[self.top_index]

    def bottom_next(self, direction=1):
        pixels[9 - 2 * self.bottom_index] = BLACK
        self.bottom_index += direction
        if direction > 0:
            if self.bottom_index == len(self.conversions):
                self.bottom_index = 0
        else:
            if self.bottom_index == -1:
                self.bottom_index = len(self.conversions) - 1

        pixels[9 - 2 * self.bottom_index] = YELLOW
        self.bottom_unit = self.conversions[self.bottom_index]

    def clear(self):
        self.input = 0
        self.decimal_place = 0
        self.dot_added = False


async def check_keys(shared):  # Don't forget the async!
    while True:
        shared.update_displays()
        if (keypress.value) == False:
            key = bottom_disp.read()
            if key:
                print(key)
                if key == "blue_btn":
                    press_start = time.monotonic()
                    was_held = False
                    while bottom_disp.read() == "blue_btn" and was_held == False:
                        if time.monotonic() - press_start > 0.25:
                            was_held = True
                            # shared.next_volume(-1)
                            # print("blue held")
                    if not was_held:
                        if shared.toggle_up:
                            shared.next_volume()
                        else:
                            shared.top_next()

                elif key == "green_btn":
                    # shared.next_volume(-1)
                    if shared.toggle_up:
                        shared.clear()
                    else:
                        shared.bottom_next()

                elif key == "decimal":
                    if shared.dot_added is False:
                        shared.dot_added = True
                elif key == "minus":
                    shared.clear()
                elif key < 0:
                    shared.skip_rebound = True
                else:
                    if shared.skip_rebound:
                        shared.skip_rebound = False
                    else:
                        if shared.dot_added:
                            shared.decimal_place += 1
                            if shared.decimal_place <= shared.converter.decimals:
                                shared.input = shared.input + int(key) * fractions[shared.decimal_place]
                            else:
                                print("stairway denied")
                                shared.decimal_place -= 1
                        else:
                            shared.input = shared.input * 10 + int(key)
                shared.update_displays()
        if shared.pwr_btn.value == 0:
            if shared.toggle_up:
                shared.top_disp.text(shared.ingredient.title, "")
                shared.btm_disp.text(shared.ingredient.title2)
                while shared.pwr_btn.value == 0:
                    shared.blink_disp.dim(False)
                    key = bottom_disp.read()
                    if key and 0 < int(key) < 10:
                        shared.ingredient = shared.ingredients[int(key) - 1]
                        shared.top_disp.text(shared.ingredient.title, front_zeros=False)
                        shared.btm_disp.text(shared.ingredient.title2, front_zeros=False)
                        while bottom_disp.read():
                            time.sleep(0.001)
                        time.sleep(0.2)
            else:
                shared.clear()
        await asyncio.sleep(0)


async def check_toggle(shared):  # Don't forget the async!
    while True:
        if shared.toggle_up != toggle.value:
            shared.toggle_up = toggle.value
            shared.update_displays()
            if shared.toggle_up:
                pixels[9 - 2 * shared.top_index - 1] = BLACK
                pixels[9 - 2 * shared.bottom_index] = BLACK
                pixels[9 - 2 * shared.mode - 1] = RED
                pixels[9 - 2 * shared.mode] = RED
            else:
                pixels[9 - 2 * shared.mode - 1] = BLACK
                pixels[9 - 2 * shared.mode] = BLACK
                pixels[9 - 2 * shared.top_index - 1] = RED
                pixels[9 - 2 * shared.bottom_index] = YELLOW
        await asyncio.sleep(0)


async def blink(interval, shared):  # Don't forget the async!
    while True:
        pixels.show()
        shared.top_disp.dim(True)
        await asyncio.sleep(interval)  # Don't forget the await!

        pixels.show()
        shared.top_disp.dim(False)
        await asyncio.sleep(interval)  # Don't forget the await!


async def main():  # Don't forget the async!
    shared = Shared(top_disp, bottom_disp, pwr_btn)
    key_task = asyncio.create_task(check_keys(shared))
    blink_task = asyncio.create_task(blink(0.20, shared))
    toggle_task = asyncio.create_task(check_toggle(shared))
    await asyncio.gather(key_task, blink_task, toggle_task)  # Don't forget the await!


asyncio.run(main())
