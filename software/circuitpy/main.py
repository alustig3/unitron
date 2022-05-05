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
import rotaryio


pixel_pin = board.SCK
num_pixels = 6
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1)
RED_dim = (64, 0, 0)
YELLOW_dim = (64, 27, 0)
RED = (128, 0, 0)
YELLOW = (128, 54, 0)
BLACK = (0, 0, 0)
pixels.fill(BLACK)
pixels.show()
fractions = (1, 0.1, 0.01, 0.001, 0.0001, 0.00001)


class Knob:
    def __init__(self, pin1, pin2):
        self.encoder = rotaryio.IncrementalEncoder(pin1, pin2)
        self.last_pos = 0

    def read(self):
        change = 0
        if self.encoder.position > self.last_pos:
            change = 1
        elif self.encoder.position < self.last_pos:
            change = -1
        self.last_pos = self.encoder.position
        return change


pwr_btn = DigitalInOut(board.TX)
pwr_btn.direction = Direction.INPUT
pwr_btn.pull = Pull.UP

encoder_btn = DigitalInOut(board.A3)
encoder_btn.direction = Direction.INPUT
encoder_btn.pull = Pull.UP

keypress = DigitalInOut(board.A1)
keypress.direction = Direction.INPUT
keypress.pull = Pull.UP

toggle = DigitalInOut(board.RX)
toggle.direction = Direction.INPUT
toggle.pull = Pull.UP

display_brightness = 9  # 0-15
numDigits = 8
i2cbus = busio.I2C(board.SCL, board.SDA, frequency=1_000_000)

pixels[0] = BLACK
try:
    i2c_device = I2CDevice(i2cbus, 0)
    with i2c_device as bus_device:
        bus_device.write(bytes([driver.SHUTDOWN, 0x01]))
        bus_device.write(bytes([driver.DECODE, 0x00]))
        bus_device.write(bytes([driver.KEYSCAN, numDigits - 1]))
        bus_device.write(bytes([driver.INTENSITY, display_brightness]))
        bus_device.write(bytes([0x2D, 0x01]))  # set self addressing mode
    time.sleep(0.12)
    print("fresh start up with address 0")
except ValueError:
    print("already self-addressing")
top_disp = driver.SegmentDisplay(1, i2cbus)
bottom_disp = driver.SegmentDisplay(3, i2cbus)

top_disp.wake()
bottom_disp.wake()


class Ingredient:
    def __init__(self, factor, title, title2="        "):
        self.title = title
        self.title2 = title2
        self.factor = factor
        self.decimals = 4

    def from_tsp(self, teaspoons):
        return teaspoons * self.factor

    def to_tsp(self, input):
        return input / self.factor


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

        flour = Ingredient(2.7083, "flour")
        sugar = Ingredient(4.167, "sugar")
        butter = Ingredient(4.708, "butter")
        cocoa = Ingredient(2, "cocoa")
        baking_powder = Ingredient(4.8, "baking", "pouuder ")
        bread_flour = Ingredient(3.2708, "bread", "flour")
        milk = Ingredient(4.0417, "nnilk")
        oil = Ingredient(4.5333, "oil")
        salt = Ingredient(6, "salt")
        self.ingredients = [baking_powder, bread_flour, butter, cocoa, flour, milk, oil, salt, sugar]
        self.ingredient_index = 0
        self.ingredient = self.ingredients[self.ingredient_index]

        cup_tsp = Linear(48, 4)  # customary cup
        tbsp_tsp = Linear(3, 4)
        tsp_tsp = Linear(1, 4)
        oz_tsp = Linear(6, 4)
        ml_tsp = Linear(0.202884, 4)
        self.conversions = [cup_tsp, tbsp_tsp, tsp_tsp, oz_tsp, ml_tsp, self.ingredient]
        self.top_index = 0
        self.bottom_index = 1
        self.top_unit = self.conversions[0]
        self.bottom_unit = self.conversions[1]

        self.converter = self.conversions[0]
        self.mode = 0
        self.dot_added = False
        self.decimal_place = 0
        self.pwr_btn = power_button
        pixels[num_pixels - 1 - self.top_index] = RED
        pixels[num_pixels - 1 - self.bottom_index] = YELLOW
        self.count = 0
        self.negative_input = False
        self.skip_rebound = False

        self.knob = Knob(board.MOSI, board.MISO)

    def update_displays(self):
        if self.toggle_up:
            self.top_disp.display(self.input, self.converter.decimals, self.dot_added)
            output = self.bottom_unit.from_tsp(self.top_unit.to_tsp(self.input))
            self.btm_disp.display(output, 4, self.dot_added)
        else:
            self.btm_disp.display(self.input, self.converter.decimals, self.dot_added)
            output = self.top_unit.from_tsp(self.bottom_unit.to_tsp(self.input))
            self.top_disp.display(output, 4, self.dot_added)

    def next_volume(self, direction=1):
        pixels[num_pixels - 1 - 2 * self.mode] = BLACK
        pixels[num_pixels - 1 - 2 * self.mode - 1] = BLACK
        self.mode += direction
        if direction > 0:
            if self.mode == len(self.conversions):
                self.mode = 0
        else:
            if self.mode == -1:
                self.mode = len(self.conversions) - 1

        self.converter = self.conversions[self.mode]
        pixels[num_pixels - 1 - 2 * self.mode - 1] = RED
        pixels[num_pixels - 1 - 2 * self.mode] = YELLOW

    def check_collision(self, direction):
        if self.top_index == self.bottom_index:
            self.top_index += direction

    def change_unit(self, location, direction):
        if location == "top":
            pixels[num_pixels - 1 - self.top_index] = BLACK
            self.top_index += direction
            if self.top_index >= len(self.conversions) or self.top_index < 0:
                self.top_index -= len(self.conversions) * direction
                if self.top_index == self.bottom_index:
                    self.top_index += direction
            if self.top_index == self.bottom_index:
                self.top_index += direction
                if self.top_index >= len(self.conversions) or self.top_index < 0:
                    self.top_index -= len(self.conversions) * direction
            pixels[num_pixels - 1 - self.top_index] = RED
        elif location == "btm":
            pixels[num_pixels - 1 - self.bottom_index] = BLACK
            self.bottom_index += direction
            if self.bottom_index >= len(self.conversions) or self.bottom_index < 0:
                self.bottom_index -= len(self.conversions) * direction
                if self.top_index == self.bottom_index:
                    self.bottom_index += direction
            if self.top_index == self.bottom_index:
                self.bottom_index += direction
                if self.bottom_index >= len(self.conversions) or self.bottom_index < 0:
                    self.bottom_index -= len(self.conversions) * direction
            pixels[num_pixels - 1 - self.bottom_index] = YELLOW
        self.update_units()

    def change_ingredient(self, direction):
        self.ingredient_index += direction
        if self.ingredient_index > len(self.ingredients) - 1:
            self.ingredient_index -= len(self.ingredients)
        elif self.ingredient_index < 0:
            self.ingredient_index += len(self.ingredients)
        self.ingredient = self.ingredients[self.ingredient_index]
        self.conversions[-1] = self.ingredient
        self.top_disp.text(self.ingredient.title, front_zeros=False)
        self.btm_disp.text(self.ingredient.title2, front_zeros=False)
        self.update_units()

    def update_units(self):
        self.top_unit = self.conversions[self.top_index]
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
                if key == "green_btn":
                    shared.clear()

                elif key == "decimal":
                    if shared.dot_added is False:
                        shared.dot_added = True
                elif key == "minus":
                    shared.clear()
                elif key < 0:  # unrecognized input. maybe multiple keyse are being held down
                    shared.skip_rebound = True
                else:
                    if shared.skip_rebound:
                        shared.skip_rebound = False
                    else:
                        if shared.dot_added:
                            shared.decimal_place += 1
                            if shared.decimal_place <= shared.converter.decimals:
                                shared.input = shared.input + key % 10 * fractions[shared.decimal_place]
                            else:
                                print("stairway denied")
                                shared.decimal_place -= 1
                        else:
                            shared.input = shared.input * 10 + key % 10
                shared.update_displays()
        if shared.pwr_btn.value == 0:
            shared.top_disp.text(shared.ingredient.title, "")
            shared.btm_disp.text(shared.ingredient.title2, "")
            while shared.pwr_btn.value == 0:
                shared.blink_disp.dim(False)
                turned = shared.knob.read()
                if turned:
                    shared.change_ingredient(turned)
        turned = shared.knob.read()
        if turned:
            if encoder_btn.value == 1:
                if shared.toggle_up:
                    shared.change_unit("top", turned)
                else:
                    shared.change_unit("btm", turned)
            else:
                if shared.toggle_up == 0:
                    shared.change_unit("top", turned)
                else:
                    shared.change_unit("btm", turned)
        await asyncio.sleep(0)


async def check_toggle(shared):
    while True:
        if shared.toggle_up != toggle.value:
            shared.toggle_up = toggle.value
            shared.update_displays()
        await asyncio.sleep(0)


async def blink(interval, shared):
    while True:
        if shared.toggle_up:
            pixels.show()
            shared.top_disp.dim(True)
            pixels[num_pixels - 1 - shared.top_index] = BLACK
            await asyncio.sleep(interval)

            pixels.show()
            shared.top_disp.dim(False)
            pixels[num_pixels - 1 - shared.top_index] = RED
            pixels[num_pixels - 1 - shared.bottom_index] = YELLOW
        else:
            pixels.show()
            shared.btm_disp.dim(True)
            pixels[num_pixels - 1 - shared.bottom_index] = BLACK
            await asyncio.sleep(interval)

            pixels.show()
            shared.btm_disp.dim(False)
            pixels[num_pixels - 1 - shared.top_index] = RED
            pixels[num_pixels - 1 - shared.bottom_index] = YELLOW

        await asyncio.sleep(interval)


async def main():  # Don't forget the async!
    shared = Shared(top_disp, bottom_disp, pwr_btn)
    key_task = asyncio.create_task(check_keys(shared))
    blink_task = asyncio.create_task(blink(0.20, shared))
    toggle_task = asyncio.create_task(check_toggle(shared))
    await asyncio.gather(key_task, blink_task, toggle_task)


asyncio.run(main())
