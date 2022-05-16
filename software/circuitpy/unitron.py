import time
import alarm
import busio
import rotaryio
import board
import as1115 as driver
import neopixel
from adafruit_bus_device.i2c_device import I2CDevice
from digitalio import DigitalInOut, Direction, Pull
from conversions import ingredients, conversions

RED = (128, 0, 0)
YELLOW = (128, 54, 0)
BLACK = (0, 0, 0)

pixel_pin = board.SCK
num_pixels = 6
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1)
pixels.fill(BLACK)
pixels.show()


class Knob:
    def __init__(self, enc_pin_1, enc_pin_2, btn_pin):
        self.encoder = rotaryio.IncrementalEncoder(enc_pin_1, enc_pin_2)
        self.last_pos = 0
        self.btn = DigitalInOut(btn_pin)
        self.btn.switch_to_input(Pull.UP)

    def read(self):
        change = self.encoder.position - self.last_pos
        self.last_pos += change
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
                # bus_device.write(bytes([driver.INTENSITY, display_brightness]))
                bus_device.write(bytes([0x2D, 0x01]))  # set self addressing mode
            time.sleep(0.12)
            print("fresh start up with address 0")
        except ValueError:
            print("already self-addressing")

        self.top_disp = driver.SegmentDisplay(1, i2cbus)
        self.btm_disp = driver.SegmentDisplay(3, i2cbus)
        self.top_disp.wake()
        self.btm_disp.wake()

        self.knob = Knob(board.MOSI, board.MISO, board.A3)

        self.pwr_btn = DigitalInOut(board.TX)
        self.pwr_btn.switch_to_input(Pull.UP)

        self.keypress = DigitalInOut(board.A1)
        self.keypress.switch_to_input(Pull.UP)

        self.toggle = DigitalInOut(board.RX)
        self.toggle.switch_to_input(Pull.UP)

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


class Interface:
    def __init__(self):
        self.toggle_up = True
        self.input = 0
        self.output = 0

        self.ingredient_index = 0
        self.ingredient = ingredients[self.ingredient_index]

        self.top_index = 0
        self.bottom_index = 5
        self.top_unit = conversions[self.top_index]
        self.bottom_unit = conversions[self.bottom_index]

        self.converter = conversions[0]
        self.mode = 0
        self.dot_added = False
        self.decimal_place = 0
        pixels[num_pixels - 1 - self.top_index] = RED
        pixels[num_pixels - 1 - self.bottom_index] = YELLOW
        self.count = 0
        self.negative_input = False
        self.skip_rebound = False

    def run_conversion(self):
        if self.toggle_up:
            self.output = self.bottom_unit.from_tsp(self.top_unit.to_tsp(self.input))
        else:
            self.output = self.top_unit.from_tsp(self.bottom_unit.to_tsp(self.input))

    def change_unit(self, location, direction):
        if location == "top":
            pixels[num_pixels - 1 - self.top_index] = BLACK
            self.top_index += direction
            if self.top_index >= len(conversions) or self.top_index < 0:
                self.top_index -= len(conversions) * direction
                if self.top_index == self.bottom_index:
                    self.top_index += direction
            if self.top_index == self.bottom_index:
                self.top_index += direction
                if self.top_index >= len(conversions) or self.top_index < 0:
                    self.top_index -= len(conversions) * direction
            pixels[num_pixels - 1 - self.top_index] = RED
        elif location == "btm":
            pixels[num_pixels - 1 - self.bottom_index] = BLACK
            self.bottom_index += direction
            if self.bottom_index >= len(conversions) or self.bottom_index < 0:
                self.bottom_index -= len(conversions) * direction
                if self.top_index == self.bottom_index:
                    self.bottom_index += direction
            if self.top_index == self.bottom_index:
                self.bottom_index += direction
                if self.bottom_index >= len(conversions) or self.bottom_index < 0:
                    self.bottom_index -= len(conversions) * direction
            pixels[num_pixels - 1 - self.bottom_index] = YELLOW
        self.update_units()

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
        self.input = 0
        self.decimal_place = 0
        self.dot_added = False