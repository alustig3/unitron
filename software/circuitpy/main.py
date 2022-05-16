# https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/usage
import asyncio
from unitron import Physical, Interface, pixels, RED, YELLOW, BLACK

unitron = Physical()
interface = Interface()

fractions = (1, 0.1, 0.01, 0.001, 0.0001, 0.00001)


async def check_inputs():
    while True:
        if (unitron.keypress.value) == False:
            key = unitron.btm_disp.read()
            if key:
                if key == "green_btn":
                    interface.clear()
                elif key == "minus":
                    # interface.clear()
                    unitron.sleep()
                elif key == "decimal":
                    if interface.dot_added is False:
                        interface.dot_added = True
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

        if unitron.pwr_btn.value == 0:
            if interface.top_index == 5 or interface.bottom_index == 5:
                unitron.top_disp.text(interface.ingredient.title, "")
                unitron.btm_disp.text(interface.ingredient.title2, "")
                while unitron.pwr_btn.value == 0:
                    unitron.top_disp.dim(False)
                    unitron.btm_disp.dim(False)
                    turned = unitron.knob.read()
                    if turned:
                        interface.change_ingredient(turned)
                        unitron.top_disp.text(interface.ingredient.title, right_justify=False)
                        unitron.btm_disp.text(interface.ingredient.title2, right_justify=False)
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

        await asyncio.sleep(0)


async def show():
    while True:
        if interface.toggle_up:
            unitron.top_disp.number(interface.input)
            unitron.btm_disp.number(interface.output)
        else:
            unitron.top_disp.number(interface.output)
            unitron.btm_disp.number(interface.input)
        await asyncio.sleep(0)


async def blink(interval):
    num_pixels = 6
    while True:
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


async def main():
    inputs_task = asyncio.create_task(check_inputs())
    show_task = asyncio.create_task(show())
    blink_task = asyncio.create_task(blink(0.20))
    await asyncio.gather(inputs_task, show_task, blink_task)


asyncio.run(main())
