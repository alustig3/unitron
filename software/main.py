# https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/usage
import microcontroller
import asyncio
import time
from unitron import Physical, Interface, RED, YELLOW, BLACK, GREEN
from settings import beep_num


unitron = Physical()
start_opposite = unitron.btm_disp.read() == "mode_btn"
interface = Interface(unitron, start_opposite)


def timer_mode():
    interface.mode = "timer"
    interface.top = "0"
    interface.btm = ""
    unitron.top_disp.dim(False)
    unitron.btm_disp.dim(False)
    unitron.pixels.fill(0)
    unitron.pixels.show()
    interface.mode_switch = True
    unitron.top_disp.text(" tiMmer ")
    unitron.btm_disp.text("        ")
    time.sleep(0.75)


def converter_mode():
    interface.clear()
    interface.mode = "converter"
    unitron.top_disp.dim(False)
    unitron.btm_disp.dim(False)
    unitron.top_disp.text("Convert ")
    unitron.btm_disp.text("        ")
    time.sleep(0.75)
    interface.run_conversion()


async def check_inputs():
    unitron.top_disp.text("Unitron ")
    unitron.btm_disp.text("        ")
    time.sleep(0.75)

    if interface.mode == "timer":
        timer_mode()
    elif interface.mode == "converter":
        converter_mode()
    while True:
        if interface.mode == "converter":
            if (unitron.keypress.value) == False:
                key = unitron.btm_disp.read()
                if key:
                    if key == "clear_btn":
                        if interface.toggle_up:
                            unitron.top_disp.clear(interface.top)
                        else:
                            unitron.btm_disp.clear(interface.top)
                        time.sleep(0.2)
                        interface.clear()
                    elif key == "mode_btn":
                        timer_mode()
                    elif key == ".":
                        if interface.digits_after_decimal < 0 and len(interface.top) < 3:
                            interface.digits_after_decimal += 1
                            interface.top += key
                    elif key == "ingredient_btn":
                        if interface.top_index == 5 or interface.bottom_index == 5:
                            unitron.top_disp.text(interface.ingredient.title, "")
                            unitron.btm_disp.text(interface.ingredient.title2, "")
                            while unitron.btm_disp.read() == "ingredient_btn":
                                unitron.top_disp.dim(False)
                                unitron.btm_disp.dim(False)
                                turned = unitron.knob.read()
                                if turned:
                                    interface.change_ingredient(turned)
                                    unitron.top_disp.text(interface.ingredient.title, right_justify=False)
                                    unitron.btm_disp.text(interface.ingredient.title2, right_justify=False)
                                interface.run_conversion()
                            # save the ingredient index to non-volatile memory so Unitron will startup using the last used ingredient
                            microcontroller.nvm[0] = interface.ingredient_index

                    elif key == "unknown":  # unrecognized input. maybe multiple keys are being held down
                        interface.skip_rebound = True
                    elif key == "release":
                        pass
                    else:
                        if interface.skip_rebound:
                            interface.skip_rebound = False
                        else:
                            if interface.top == "0" and key != ".":
                                # replace  0 with new number
                                interface.top = str(key)
                            else:
                                if interface.digits_after_decimal < 2:
                                    if interface.digits_after_decimal > -1:
                                        if float(interface.top) < 10000:
                                            interface.digits_after_decimal += 1
                                            interface.top += str(key)
                                    elif 10 * float(interface.top) < 10000:
                                        interface.top += str(key)
                    if interface.mode == "converter":
                        interface.run_conversion()

            # check for knob rotation
            turned = unitron.knob.read()
            if turned:
                # rotating changes blinking input unit
                if unitron.knob.btn.value == 1:
                    interface.change_unit(interface.toggle_up, turned)

                # rotating while pressing changes output unit
                else:
                    interface.change_unit(not interface.toggle_up, turned)
                interface.run_conversion()

            if interface.toggle_up != unitron.toggle.value:
                interface.toggle_up = unitron.toggle.value
                interface.run_conversion()

        elif interface.mode == "timer":
            if (unitron.keypress.value) == False:
                # p = unitron.battery_lvl.value / 65535 * 3.3 * 2
                # interface.top = p
                key = unitron.btm_disp.read()
                if key and interface.is_ticking == False:
                    if key == "clear_btn":
                        unitron.top_disp.clear(interface.top)
                        time.sleep(0.2)
                        interface.clear()
                    elif key == "mode_btn":
                        converter_mode()
                    elif key == ".":
                        if interface.dot_added < 3 and interface.top[-1] != ".":
                            interface.dot_added += 1
                            interface.top += str(key)
                    elif key == "ingredient_btn":
                        pass
                    elif key == "unknown":  # unrecognized input. maybe multiple keys are being held down
                        interface.skip_rebound = True
                    elif key == "release":
                        pass
                    else:
                        if interface.skip_rebound:
                            interface.skip_rebound = False
                        else:
                            if interface.top == "0" and key != ".":
                                interface.top = str(key)
                            else:
                                interface.top += str(key)
            if interface.toggle_up != unitron.toggle.value:
                interface.toggle_up = unitron.toggle.value
                seconds_on_clock = interface.clock_str_to_seconds(interface.top)
                if seconds_on_clock > 0:
                    interface.is_ticking = not interface.is_ticking
                    if interface.is_ticking:
                        if interface.clock_percentage != 0:
                            pass
                        else:
                            interface.top = interface.seconds_to_clock_str(seconds_on_clock)
                            interface.btm = interface.top
                            interface.clock_percentage = 0
                            unitron.pixels.fill(0)
        await asyncio.sleep(0)


async def show():
    while True:
        if interface.mode == "converter":
            if interface.toggle_up:
                unitron.top_disp.text((interface.top))
                unitron.btm_disp.text((interface.btm))
            else:
                unitron.top_disp.text((interface.btm))
                unitron.btm_disp.text((interface.top))
            await asyncio.sleep(0)
        else:
            unitron.top_disp.time(interface.top)
            unitron.btm_disp.time(interface.btm)
            await asyncio.sleep(0)


async def blink(interval):
    num_pixels = 6
    while True:
        if interface.mode == "converter":
            if interface.toggle_up:
                unitron.top_disp.dim(True)
                interface.indicator("top", BLACK)
                await asyncio.sleep(interval)

                unitron.top_disp.dim(False)
                if interface.mode == "converter":
                    interface.indicator("top", RED)
                    interface.indicator("bottom", YELLOW)
            else:
                unitron.btm_disp.dim(True)
                interface.indicator("bottom", BLACK)
                await asyncio.sleep(interval)

                unitron.btm_disp.dim(False)
                if interface.mode == "converter":
                    interface.indicator("top", RED)
                    interface.indicator("bottom", YELLOW)
        elif interface.mode_switch:
            unitron.pixels.fill(0)
            unitron.pixels.show()
            interface.mode_switch = False

        await asyncio.sleep(interval)


async def tick():
    while True:
        if interface.mode == "timer" and interface.is_ticking:
            total = interface.clock_str_to_seconds(interface.top)
            if total <= 0:
                for _ in range(beep_num):
                    for _ in range(4):
                        if interface.is_ticking:
                            unitron.speaker.value = True
                            unitron.pixels.fill(GREEN)
                            await asyncio.sleep(beep_length := 0.05)
                            unitron.speaker.value = False
                            unitron.pixels.fill(BLACK)
                            await asyncio.sleep(beep_length)
                    if interface.is_ticking:
                        await asyncio.sleep(5 * beep_length)
                interface.is_ticking = False
                interface.top = interface.btm
                await asyncio.sleep(0)
            else:
                await asyncio.sleep(1)
                if interface.is_ticking:
                    total -= 1
                    interface.clock_percentage = 1 - total / interface.clock_str_to_seconds(interface.btm)
                    progress = interface.clock_percentage * 1530
                    interface.top = interface.seconds_to_clock_str(total)
                    if progress >= 1275:
                        unitron.pixels[5] = (0, 255, 0)
                        unitron.pixels[4] = (0, 255, 0)
                        unitron.pixels[3] = (0, 255, 0)
                        unitron.pixels[2] = (0, 255, 0)
                        unitron.pixels[1] = (0, 255, 0)
                        unitron.pixels[0] = (0, progress % 255, 0)
                    elif progress >= 1020:
                        unitron.pixels[5] = (0, 255, 0)
                        unitron.pixels[4] = (0, 255, 0)
                        unitron.pixels[3] = (0, 255, 0)
                        unitron.pixels[2] = (0, 255, 0)
                        unitron.pixels[1] = (0, progress % 255, 0)
                    elif progress >= 765:
                        unitron.pixels[5] = (0, 255, 0)
                        unitron.pixels[4] = (0, 255, 0)
                        unitron.pixels[3] = (0, 255, 0)
                        unitron.pixels[2] = (0, progress % 255, 0)
                    elif progress >= 510:
                        unitron.pixels[5] = (0, 255, 0)
                        unitron.pixels[4] = (0, 255, 0)
                        unitron.pixels[3] = (0, progress % 255, 0)
                    elif progress >= 255:
                        unitron.pixels[5] = (0, 255, 0)
                        unitron.pixels[4] = (0, progress % 255, 0)
                    else:
                        unitron.pixels[5] = (0, progress % 255, 0)

                    unitron.pixels.show()
        else:
            await asyncio.sleep(0)


async def main():
    inputs_task = asyncio.create_task(check_inputs())
    blink_task = asyncio.create_task(blink(0.20))
    show_task = asyncio.create_task(show())
    tick_task = asyncio.create_task(tick())
    await asyncio.gather(inputs_task, blink_task, show_task, tick_task)


asyncio.run(main())
