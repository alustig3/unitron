import microcontroller
import time
import alarm
import busio
import rotaryio
import board
import as1115 as driver
import neopixel
import math
import re
from adafruit_bus_device.i2c_device import I2CDevice
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
from conversions import conversions
from settings import start_mode, ingredients

RED = (128, 0, 0)
GREEN = (0, 128, 0)
YELLOW = (128, 54, 0)
BLACK = (0, 0, 0)

regex = re.compile("\.")


class Knob:
    def __init__(self, enc_pin_1, enc_pin_2, btn_pin):
        self.encoder = rotaryio.IncrementalEncoder(enc_pin_1, enc_pin_2)
        self.last_pos = 0
        self.btn = DigitalInOut(btn_pin)
        self.btn.switch_to_input(Pull.UP)

    def read(self):
        change = self.encoder.position - self.last_pos
        if change > 0:
            change = 1
        elif change < 0:
            change = -1
        self.last_pos += change
        time.sleep(0.01)
        return change


class Physical:
    def __init__(self):
        numDigits = 8
        i2cbus = busio.I2C(board.SCL, board.SDA, frequency=1_000_000)
        try:
            i2c_device = I2CDevice(i2cbus, 0)
            with i2c_device as bus_device:
                bus_device.write(bytes([driver.SHUTDOWN, 0x01]))
                bus_device.write(bytes([driver.DECODE, 0x00]))
                bus_device.write(bytes([driver.KEYSCAN, numDigits - 1]))
                bus_device.write(bytes([driver.INTENSITY, 10]))
                bus_device.write(bytes([0x2D, 0x01]))  # set self addressing mode
            time.sleep(0.12)
            print("fresh start up with address 0")
        except ValueError:
            print("already self-addressing")

        pixel_pin = board.SCK
        self.num_pixels = 6
        self.pixels = neopixel.NeoPixel(pixel_pin, self.num_pixels, brightness=0.1)
        self.pixels.fill(BLACK)
        self.pixels.show()

        self.top_disp = driver.SegmentDisplay(1, i2cbus)
        self.btm_disp = driver.SegmentDisplay(3, i2cbus)
        self.top_disp.wake()
        self.btm_disp.wake()

        self.knob = Knob(board.MOSI, board.MISO, board.A3)

        self.speaker = DigitalInOut(board.RX)
        self.speaker.direction = Direction.OUTPUT
        self.speaker.value = 0

        self.keypress = DigitalInOut(board.A1)
        self.keypress.switch_to_input(Pull.UP)

        self.toggle = DigitalInOut(board.TX)
        self.toggle.switch_to_input(Pull.UP)

        self.battery_lvl = AnalogIn(board.A2)

    def sleep(self):
        self.pwr_btn.deinit()
        pin_alarm = alarm.pin.PinAlarm(pin=board.TX, value=False, pull=True)
        self.top_disp.sleep()
        self.btm_disp.sleep()
        self.pixels.fill(0)

        # alarm.light_sleep_until_alarms(time_alarm)
        alarm.exit_and_deep_sleep_until_alarms(pin_alarm)

        self.pwr_btn = DigitalInOut(board.TX)
        self.pwr_btn.direction = Direction.INPUT
        self.pwr_btn.pull = Pull.UP
        self.top_disp.wake()
        self.btm_disp.wake()


class Interface:
    def __init__(self, unitron, start_opposite):
        self.toggle_up = True
        self.top = "0"
        self.btm = "0"

        self.ingredient_index = microcontroller.nvm[0]  # recall the last used ingredient from non-volatile memory
        try:
            self.ingredient = ingredients[self.ingredient_index]
        except IndexError:
            self.ingredient_index = 0
        self.ingredient = ingredients[self.ingredient_index]

        self.top_index = 0
        self.bottom_index = 5
        self.top_unit = conversions[self.top_index]
        self.bottom_unit = conversions[self.bottom_index]

        self.converter = conversions[0]
        if start_opposite:
            if start_mode == "converter":
                self.mode = "timer"
            else:
                self.mode = "converter"
        else:
            self.mode = start_mode
        self.digits_after_decimal = -1
        self.dot_added = 0

        self.unitron = unitron
        self.indicator("top", BLACK)
        self.indicator("bottom", BLACK)
        self.count = 0
        self.negative_input = False
        self.skip_rebound = False

        self.is_ticking = False
        self.clock_percentage = 0
        self.mode_switch = False

    def run_conversion(self):
        if self.toggle_up:
            self.btm = self.bottom_unit.from_tsp(self.top_unit.to_tsp(self.top))
            if len(self.btm) > 8:
                self.top = self.top[:-1]
                self.btm = self.bottom_unit.from_tsp(self.top_unit.to_tsp(self.top))
        else:
            self.btm = self.top_unit.from_tsp(self.bottom_unit.to_tsp(self.top))
            if len(self.btm) > 8:
                self.top = self.top[:-1]
                self.btm = self.top_unit.from_tsp(self.bottom_unit.to_tsp(self.top))

    def change_unit(self, toggle_is_up, direction):
        if toggle_is_up:
            self.indicator("top", BLACK)
            self.top_index += direction
            if self.top_index >= len(conversions) or self.top_index < 0:
                self.top_index -= len(conversions) * direction
                if self.top_index == self.bottom_index:
                    self.top_index += direction
            if self.top_index == self.bottom_index:
                self.top_index += direction
                if self.top_index >= len(conversions) or self.top_index < 0:
                    self.top_index -= len(conversions) * direction
            self.indicator("top", RED)
        else:
            self.indicator("bottom", BLACK)
            self.bottom_index += direction
            if self.bottom_index >= len(conversions) or self.bottom_index < 0:
                self.bottom_index -= len(conversions) * direction
                if self.top_index == self.bottom_index:
                    self.bottom_index += direction
            if self.top_index == self.bottom_index:
                self.bottom_index += direction
                if self.bottom_index >= len(conversions) or self.bottom_index < 0:
                    self.bottom_index -= len(conversions) * direction
            self.indicator("bottom", YELLOW)
        self.update_units()

    def indicator(self, location, color):
        if location == "top":
            location = self.top_index
        else:
            location = self.bottom_index
        self.unitron.pixels[self.unitron.num_pixels - 1 - location] = color

    def change_ingredient(self, direction):
        self.ingredient_index += direction
        if self.ingredient_index > len(ingredients) - 1:
            self.ingredient_index -= len(ingredients)
        elif self.ingredient_index < 0:
            self.ingredient_index += len(ingredients)
        self.ingredient = ingredients[self.ingredient_index]
        conversions[-1] = self.ingredient
        self.update_units()

    def update_units(self):
        self.top_unit = conversions[self.top_index]
        self.bottom_unit = conversions[self.bottom_index]

    def clear(self):
        self.top = "0"
        self.btm = "0"
        self.digits_after_decimal = -1
        self.dot_added = 0
        self.clock_percentage = 0
        self.unitron.pixels.fill(0)

    def add_to_clock(self, new_digit):
        print("new_digit", new_digit)
        if self.top == "0" and new_digit != ".":
            self.top = str(new_digit)
        else:
            self.top += str(new_digit)

    def clock_str_to_seconds(self, clock):
        if clock[-1] == ".":  # remove trailing decimal
            clock = clock[:-1]
        hrs, mins, secs = 0, 0, 0
        times = regex.split(clock)
        if len(times) == 3:
            hrs, mins, secs = times
        elif len(times) == 2:
            mins, secs = times
        else:
            secs = times[0]

        return int(hrs) * 3600 + int(mins) * 60 + int(secs)

    def seconds_to_clock_str(self, seconds):
        hrs = math.floor(seconds / 3600)
        seconds %= 3600
        mins = math.floor(seconds / 60)
        seconds %= 60
        if hrs:
            return f"{hrs}.{mins:02d}.{seconds:02d}"
        elif mins:
            return f"{mins}.{seconds:02d}"
        else:
            return f"{seconds}"
