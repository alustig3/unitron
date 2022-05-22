alphabet = {
    "a": 119,
    "b": 31,
    "c": 78,
    "d": 61,
    "e": 79,
    "f": 71,
    # "g": 95,
    "g": 123,
    "h": 23,
    "i": 16,
    "k": 55,
    "l": 14,
    "n": 21,
    "o": 29,
    # "o": 126,
    "p": 103,
    "q": 115,
    "r": 5,
    "s": 91,
    "t": 15,
    "u": 28,
    " ": 0,
    "0": 126,
    "1": 48,
    "2": 109,
    "3": 121,
    "4": 51,
    "5": 91,
    "6": 95,
    "7": 112,
    "8": 127,
    "9": 123,
    "-": 1,
}

SHUTDOWN = 0x0C
KEYSCAN = 0x0B
INTENSITY = 0x0A
FEATURE = 0x0E
DECODE = 0x09
KEYA = 0x1C
KEYB = 0x1D


def normal_round(num, ndigits=0):
    if ndigits == 0:
        return int(num + 0.5)
    else:
        digit_value = 10 ** ndigits
        return int(num * digit_value + 0.5) / digit_value


class SegmentDisplay:
    def __init__(self, address, i2c):
        # The follow is for I2C communications
        self.address = address
        self.i2c = i2c

    def text(self, word_array, right_justify=True):
        word_array = str(word_array)
        leading_blank = 8 - len(word_array)
        add_dot_at = word_array.find(".")
        if add_dot_at > 0:
            leading_blank += 1
            word_array = word_array.replace(".", "")
        if right_justify:
            word_array = leading_blank * " " + word_array
        else:
            word_array = word_array + leading_blank * " "
        if self.i2c.try_lock():
            for i, ltr in enumerate(word_array.lower()):
                temp = alphabet[ltr]
                if add_dot_at > 0 and i == (leading_blank + add_dot_at - 1):
                    temp += 128
                self.i2c.writeto(self.address, bytes([i + 1, temp]))
            self.i2c.unlock()

    def number(self, number):
        if number > 1:
            places = 2
        else:
            places = 4
        rounded_val = normal_round(number, places)
        if rounded_val == int(rounded_val):
            self.text(int(rounded_val))
        else:
            self.text(rounded_val)

    def sleep(self):
        if self.i2c.try_lock():
            self.i2c.writeto(self.address, bytes([SHUTDOWN, 0x80]))
            self.i2c.unlock()

    def wake(self):
        if self.i2c.try_lock():
            self.i2c.writeto(self.address, bytes([SHUTDOWN, 0x81]))
            self.i2c.unlock()

    def read(self):
        regA = bytearray(1)
        regB = bytearray(1)
        if self.i2c.try_lock():
            self.i2c.writeto(self.address, bytes([KEYA]))
            self.i2c.readfrom_into(self.address, regA)
            self.i2c.writeto(self.address, bytes([KEYB]))
            self.i2c.readfrom_into(self.address, regB)
            self.i2c.unlock()
            value = ~(regA[0] << 8 | regB[0]) & 0xFFFF
            if value == 4096:
                return 10
            if value == 64:
                return 1
            if value == 32:
                return 2
            if value == 16:
                return 3
            if value == 4:
                return 4
            if value == 2:
                return 5
            if value == 1:
                return 6
            if value == 8:
                return 7
            if value == 128:
                return 8
            if value == 16384:
                return 9
            if value == 1024:
                return "pwr_btn"
            if value == 2048:
                return "green_btn"
            if value == 32768:
                return "decimal"
            if value == 8192:
                return "minus"
            return -value

    def dim(self, do_dim):
        if self.i2c.try_lock():
            if do_dim:
                self.i2c.writeto(self.address, bytes([INTENSITY, 1]))
            else:
                self.i2c.writeto(self.address, bytes([INTENSITY, 10]))
            self.i2c.unlock()
