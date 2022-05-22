# https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/usage
import asyncio
import time
from unitron import Physical, Interface, pixels, RED, YELLOW, BLACK, GREEN

unitron = Physical()
interface = Interface()

fractions = (1, 0.1, 0.01, 0.001, 0.0001, 0.00001)


async def check_inputs():
    while True:
        if interface.mode == "converter":
            if (unitron.keypress.value) == False:
                key = unitron.btm_disp.read()
                if key:
                    if key == "green_btn":
                        unitron.speaker.value = 1
                        interface.clear()
                        time.sleep(0.04)
                        unitron.speaker.value = 0
                    elif key == "minus":
                        interface.mode = "timer"
                        interface.input = 0
                    elif key == "decimal":
                        if interface.dot_added is False:
                            interface.dot_added = True
                    elif key == "pwr_btn":
                        if interface.top_index == 5 or interface.bottom_index == 5:
                            unitron.top_disp.text(interface.ingredient.title, "")
                            unitron.btm_disp.text(interface.ingredient.title2, "")
                            while unitron.btm_disp.read() == "pwr_btn":
                                unitron.top_disp.dim(False)
                                unitron.btm_disp.dim(False)
                                turned = unitron.knob.read()
                                if turned:
                                    interface.change_ingredient(turned)
                                    unitron.top_disp.text(interface.ingredient.title, right_justify=False)
                                    unitron.btm_disp.text(interface.ingredient.title2, right_justify=False)
                                interface.run_conversion()

                    elif key < 0:  # unrecognized input. maybe multiple keyse are being held down
                        interface.skip_rebound = True
                    else:
                        if interface.skip_rebound:
                            interface.skip_rebound = False
                        else:
                            if interface.dot_added:
                                interface.decimal_place += 1
                                if interface.decimal_place <= 4:
                                    interface.input = interface.input + key % 10 * fractions[interface.decimal_place]
                                else:
                                    print("stairway denied")
                                    interface.decimal_place -= 1
                            else:
                                interface.input = interface.input * 10 + key % 10
                    interface.run_conversion()

            # check for knob rotation
            turned = unitron.knob.read()
            # print(unitron.knob.btn.value)
            if turned:
                # rotating changes blinking input unit
                if unitron.knob.btn.value == 1:
                    if interface.toggle_up:
                        interface.change_unit("top", turned)
                    else:
                        interface.change_unit("btm", turned)
                # rotating while pressing changes output unit
                else:
                    if interface.toggle_up:
                        interface.change_unit("btm", turned)
                    else:
                        interface.change_unit("top", turned)
                interface.run_conversion()

            if interface.toggle_up != unitron.toggle.value:
                interface.toggle_up = unitron.toggle.value
                interface.run_conversion()

        elif interface.mode == "timer":

            if (unitron.keypress.value) == False:
                # p = unitron.battery_lvl.value / 65535 * 3.3 * 2
                # interface.input = p
                key = unitron.btm_disp.read()
                if key:
                    if key == "green_btn":
                        interface.clear()
                    elif key == "minus":
                        interface.mode = "converter"
                        interface.run_conversion()
                    elif key == "decimal":
                        if interface.dot_added < 1:
                            interface.dot_added += 1
                    elif key < 0:  # unrecognized input. maybe multiple keyse are being held down
                        interface.skip_rebound = True
                    else:
                        if interface.skip_rebound:
                            interface.skip_rebound = False
                        else:
                            if interface.dot_added:
                                interface.decimal_place += 1
                                if interface.decimal_place <= 4:
                                    interface.input = interface.input + key % 10 * fractions[interface.decimal_place]
                                else:
                                    print("stairway denied")
                                    interface.decimal_place -= 1
                            else:
                                interface.input = interface.input * 10 + key % 10
            if interface.toggle_up != unitron.toggle.value:
                interface.toggle_up = unitron.toggle.value
                interface.is_ticking = not interface.is_ticking
                if interface.is_ticking:
                    interface.output = interface.input
                    interface.clock_percentage = 0
                    pixels.fill(0)
        await asyncio.sleep(0)


async def show():
    while True:
        if interface.mode == "converter":
            if interface.toggle_up:
                unitron.top_disp.number(interface.input)
                unitron.btm_disp.number(interface.output)
            else:
                unitron.top_disp.number(interface.output)
                unitron.btm_disp.number(interface.input)
            await asyncio.sleep(0)
        else:
            unitron.top_disp.number(interface.input)
            unitron.btm_disp.number(round(interface.clock_percentage*100))
            await asyncio.sleep(0)



async def blink(interval):
    num_pixels = 6
    while True:
        if interface.mode == "converter":
            if interface.toggle_up:
                unitron.top_disp.dim(True)
                pixels.show()
                pixels[num_pixels - 1 - interface.top_index] = BLACK
                await asyncio.sleep(interval)

                unitron.top_disp.dim(False)
                pixels.show()
                pixels[num_pixels - 1 - interface.top_index] = RED
                pixels[num_pixels - 1 - interface.bottom_index] = YELLOW
            else:
                unitron.btm_disp.dim(True)
                pixels.show()
                pixels[num_pixels - 1 - interface.bottom_index] = BLACK
                await asyncio.sleep(interval)

                unitron.btm_disp.dim(False)
                pixels.show()
                pixels[num_pixels - 1 - interface.top_index] = RED
                pixels[num_pixels - 1 - interface.bottom_index] = YELLOW

        await asyncio.sleep(interval)

async def tick():
    while True:
        if interface.mode == "timer" and interface.is_ticking:
            if interface.input <= 0:
                beep_length = .05
                beep_rest = 25*beep_length
                while interface.is_ticking:
                    for i in range(4):
                        unitron.speaker.value = True
                        pixels.fill(GREEN)
                        await asyncio.sleep(beep_length)
                        unitron.speaker.value = False
                        pixels.fill(BLACK)
                        await asyncio.sleep(beep_length)
                    await asyncio.sleep(beep_rest)
                    print("done!")
                    await asyncio.sleep(.3)

                interface.input = 0
                await asyncio.sleep(0)
            else:
                await asyncio.sleep(1)
                if interface.is_ticking:
                    interface.input -= 1
                    interface.clock_percentage = 1 - interface.input / interface.output
                    progress = interface.clock_percentage*1530
                    print(interface.clock_percentage,progress,progress%255)
                    if progress>=1275:
                        pixels[5] = (0,255,0)
                        pixels[4] = (0,255,0)
                        pixels[3] = (0,255,0)
                        pixels[2] = (0,255,0)
                        pixels[1] = (0,255,0)
                        pixels[0] = (0,progress%255,0)
                    elif progress>=1020:
                        pixels[5] = (0,255,0)
                        pixels[4] = (0,255,0)
                        pixels[3] = (0,255,0)
                        pixels[2] = (0,255,0)
                        pixels[1] = (0,progress%255,0)
                    elif progress>=765:
                        pixels[5] = (0,255,0)
                        pixels[4] = (0,255,0)
                        pixels[3] = (0,255,0)
                        pixels[2] = (0,progress%255,0)
                    elif progress>=510:
                        pixels[5] = (0,255,0)
                        pixels[4] = (0,255,0)
                        pixels[3] = (0,progress%255,0)
                    elif progress>=255:
                        pixels[5] = (0,255,0)
                        pixels[4] = (0,progress%255,0)
                    else:
                        pixels[5] = (0,progress%255,0)

                    pixels.show()
        else:
            await asyncio.sleep(0)



async def main():
    inputs_task = asyncio.create_task(check_inputs())
    blink_task = asyncio.create_task(blink(0.20))
    show_task = asyncio.create_task(show())
    tick_task = asyncio.create_task(tick())
    await asyncio.gather(inputs_task, blink_task, show_task)


asyncio.run(main())
