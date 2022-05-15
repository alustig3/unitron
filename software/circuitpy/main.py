# https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/usage
import time
import alarm
import asyncio
import board
import as1115 as driver
import neopixel
import busio
import rotaryio
from adafruit_bus_device.i2c_device import I2CDevice
from digitalio import DigitalInOut, Direction, Pull


display_brightness = 9  # 0-15
numDigits = 8
i2cbus = busio.I2C(board.SCL, board.SDA, frequency=1_000_000)

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
        change = self.encoder.position - self.last_pos
        self.last_pos += change
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


class Shared:
    def __init__(self, top_disp, btm_disp, power_button):
        self.toggle_up = True
        self.input = 0
        self.output = 0
        self.top_disp = top_disp
        self.btm_disp = btm_disp
        self.blink_disp = top_disp

        butter = Ingredient(4.708, "butter")
        baking_powder = Ingredient(4.8, "baking", "pouuder ")
        bread_flour = Ingredient(3.2708, "bread", "flour")
        cocoa = Ingredient(2, "cocoa")
        flour = Ingredient(2.7083, "flour")
        milk = Ingredient(4.0417, "nnilk")
        oil = Ingredient(4.5333, "oil")
        salt = Ingredient(6, "salt")
        sugar = Ingredient(4.167, "sugar")
        self.ingredients = [baking_powder, bread_flour, butter, cocoa, flour, milk, oil, salt, sugar]
        self.ingredient_index = 0
        self.ingredient = self.ingredients[self.ingredient_index]

        cup_tsp = Unit(48)  # customary cup
        tbsp_tsp = Unit(3)
        tsp_tsp = Unit(1)
        oz_tsp = Unit(6)
        ml_tsp = Unit(0.202884)
        self.conversions = [cup_tsp, tbsp_tsp, tsp_tsp, oz_tsp, ml_tsp, self.ingredient]
        self.top_index = 0
        self.bottom_index = 5
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
            self.top_disp.display(self.input)
            output = self.bottom_unit.from_tsp(self.top_unit.to_tsp(self.input))
            self.btm_disp.display(output)
        else:
            self.btm_disp.display(self.input)
            output = self.top_unit.from_tsp(self.bottom_unit.to_tsp(self.input))
            self.top_disp.display(output)

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

    def sleep(self):
        self.pwr_btn.deinit()
        pin_alarm = alarm.pin.PinAlarm(pin=board.TX, value=False, pull=True)
        self.top_disp.sleep()
        self.btm_disp.sleep()
        pixels.fill(0)

        # alarm.light_sleep_until_alarms(time_alarm)
        alarm.exit_and_deep_sleep_until_alarms(pin_alarm)

        self.pwr_btn = DigitalInOut(board.TX)
        self.pwr_btn.direction = Direction.INPUT
        self.pwr_btn.pull = Pull.UP
        self.top_disp.wake()
        self.btm_disp.wake()


async def check_keys(shared):  # Don't forget the async!
    while True:
        shared.update_displays()
        if (keypress.value) == False:
            key = bottom_disp.read()
            if key:
                if key == "green_btn":
                    shared.clear()
                elif key == "minus":
                    # shared.clear()
                    shared.top_disp.text(shared.ingredient.title, "")
                    shared.btm_disp.text(shared.ingredient.title2, "")
                    while bottom_disp.read() == "minus":
                        shared.blink_disp.dim(False)
                        turned = shared.knob.read()
                        if turned:
                            shared.change_ingredient(turned)
                            # shared.sleep()
                elif key == "decimal":
                    if shared.dot_added is False:
                        shared.dot_added = True
                elif key < 0:  # unrecognized input. maybe multiple keyse are being held down
                    shared.skip_rebound = True
                else:
                    if shared.skip_rebound:
                        shared.skip_rebound = False
                    else:
                        if shared.dot_added:
                            shared.decimal_place += 1
                            if shared.decimal_place <= 4:
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
