# https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/usage
import asyncio
import time
from unitron import Physical, Interface, pixels, RED, YELLOW, BLACK, GREEN

unitron = Physical()
interface = Interface()


async def check_inputs():
    while True:
        if interface.mode == "converter":
            if (unitron.keypress.value) == False:
                key = unitron.btm_disp.read()
                if key:
                    if key == "green_btn":
                        if interface.toggle_up:
                            unitron.top_disp.clear(interface.input)
                        else:
                            unitron.btm_disp.clear(interface.input)
                        time.sleep(0.2)
                        interface.clear()
                    elif key == "minus":
                        interface.mode = "timer"
                        interface.input = "0"
                        interface.output = ""
                        unitron.top_disp.dim(False)
                        unitron.btm_disp.dim(False)
                        pixels.fill(0)
                        pixels.show()
                        interface.mode_switch = True
                        unitron.top_disp.text(" count- ")
                        unitron.btm_disp.text(" douun  ")
                        time.sleep(0.75)
                    elif key == ".":
                        if interface.digits_after_decimal < 0 and len(interface.input) < 3:
                            interface.digits_after_decimal += 1
                            interface.input += key
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
                    elif key == "unknown":  # unrecognized input. maybe multiple keys are being held down
                        interface.skip_rebound = True
                    elif key == "release":
                        pass
                    else:
                        if interface.skip_rebound:
                            interface.skip_rebound = False
                        else:
                            if interface.input == "0" and key != ".":
                                # replace  0 with new number
                                interface.input = str(key)
                            else:
                                if interface.digits_after_decimal < 2:
                                    if interface.digits_after_decimal > -1:
                                        if float(interface.input) < 10000:
                                            interface.digits_after_decimal += 1
                                            interface.input += str(key)
                                    elif 10 * float(interface.input) < 10000:
                                        interface.input += str(key)
                    if interface.mode == "converter":
                        interface.run_conversion()

            # check for knob rotation
            turned = unitron.knob.read()
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
                        unitron.top_disp.clear(interface.input)
                        time.sleep(0.2)
                        interface.clear()
                    elif key == "minus":
                        interface.mode = "converter"
                        interface.input = "0"
                        interface.output = "0"
                        pixels.fill(0)
                        unitron.top_disp.dim(False)
                        unitron.btm_disp.dim(False)
                        unitron.top_disp.text("conuert ")
                        unitron.btm_disp.text("        ")
                        time.sleep(0.75)
                        interface.run_conversion()
                    elif key == ".":
                        if interface.dot_added < 1:
                            interface.dot_added += 1
                            interface.input += str(key)
                    elif key == "pwr_btn":
                        pass
                    elif key == "unknown":  # unrecognized input. maybe multiple keys are being held down
                        interface.skip_rebound = True
                    elif key == "release":
                        pass
                    else:
                        if interface.skip_rebound:
                            interface.skip_rebound = False
                        else:
                            if interface.input == "0" and key != ".":
                                interface.input = str(key)
                            else:
                                interface.input += str(key)
            if interface.toggle_up != unitron.toggle.value:
                interface.toggle_up = unitron.toggle.value
                interface.is_ticking = not interface.is_ticking
                if interface.is_ticking:
                    interface.output = interface.input
                    interface.clock_percentage = 0
                    pixels.fill(0)
                    pixels.show()
        await asyncio.sleep(0)


async def show():
    while True:
        if interface.mode == "converter":
            if interface.toggle_up:
                unitron.top_disp.text((interface.input))
                unitron.btm_disp.text((interface.output))
            else:
                unitron.top_disp.text((interface.output))
                unitron.btm_disp.text((interface.input))
            await asyncio.sleep(0)
        else:
            unitron.top_disp.text(interface.input)
            unitron.btm_disp.text(interface.output)
            await asyncio.sleep(0)


async def blink(interval):
    num_pixels = 6
    while True:
        if interface.mode == "converter":
            if interface.toggle_up:
                unitron.top_disp.dim(True)
                pixels[num_pixels - 1 - interface.top_index] = BLACK
                await asyncio.sleep(interval)

                unitron.top_disp.dim(False)
                if interface.mode == "converter":
                    pixels[num_pixels - 1 - interface.top_index] = RED
                    pixels[num_pixels - 1 - interface.bottom_index] = YELLOW
            else:
                unitron.btm_disp.dim(True)
                pixels[num_pixels - 1 - interface.bottom_index] = BLACK
                await asyncio.sleep(interval)

                unitron.btm_disp.dim(False)
                if interface.mode == "converter":
                    pixels[num_pixels - 1 - interface.top_index] = RED
                    pixels[num_pixels - 1 - interface.bottom_index] = YELLOW
        elif interface.mode_switch:
            pixels.fill(0)
            pixels.show()
            interface.mode_switch = False

        await asyncio.sleep(interval)


async def tick():
    while True:
        if interface.mode == "timer" and interface.is_ticking:
            if int(interface.input) <= 0:
                beep_length = 0.05
                beep_rest = 25 * beep_length
                # while interface.is_ticking:
                for _ in range(3):
                    for _ in range(4):
                        if interface.is_ticking:
                            unitron.speaker.value = True
                            pixels.fill(GREEN)
                            await asyncio.sleep(beep_length)
                            unitron.speaker.value = False
                            pixels.fill(BLACK)
                            await asyncio.sleep(beep_length)
                    if interface.is_ticking:
                        await asyncio.sleep(beep_rest)
                        print("done!")
                        await asyncio.sleep(0.3)
                interface.is_ticking = False
                interface.input = "0"
                interface.output = "0"
                await asyncio.sleep(0)
            else:
                await asyncio.sleep(1)
                if interface.is_ticking:
                    interface.input = int(interface.input) - 1
                    interface.clock_percentage = 1 - interface.input / int(interface.output)
                    progress = interface.clock_percentage * 1530
                    interface.input = str(interface.input)
                    print(interface.clock_percentage, progress, progress % 255)
                    if progress >= 1275:
                        pixels[5] = (0, 255, 0)
                        pixels[4] = (0, 255, 0)
                        pixels[3] = (0, 255, 0)
                        pixels[2] = (0, 255, 0)
                        pixels[1] = (0, 255, 0)
                        pixels[0] = (0, progress % 255, 0)
                    elif progress >= 1020:
                        pixels[5] = (0, 255, 0)
                        pixels[4] = (0, 255, 0)
                        pixels[3] = (0, 255, 0)
                        pixels[2] = (0, 255, 0)
                        pixels[1] = (0, progress % 255, 0)
                    elif progress >= 765:
                        pixels[5] = (0, 255, 0)
                        pixels[4] = (0, 255, 0)
                        pixels[3] = (0, 255, 0)
                        pixels[2] = (0, progress % 255, 0)
                    elif progress >= 510:
                        pixels[5] = (0, 255, 0)
                        pixels[4] = (0, 255, 0)
                        pixels[3] = (0, progress % 255, 0)
                    elif progress >= 255:
                        pixels[5] = (0, 255, 0)
                        pixels[4] = (0, progress % 255, 0)
                    else:
                        pixels[5] = (0, progress % 255, 0)

                    pixels.show()
        else:
            await asyncio.sleep(0)


async def main():
    inputs_task = asyncio.create_task(check_inputs())
    blink_task = asyncio.create_task(blink(0.20))
    show_task = asyncio.create_task(show())
    tick_task = asyncio.create_task(tick())
    await asyncio.gather(inputs_task, blink_task, show_task, tick_task)


asyncio.run(main())
