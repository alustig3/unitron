# Unitron

Unitron is a kitchen tool for working with important cooking units -- time, space, and mass -- using tactually-pleasing switches, knobs, and buttons, non-intrusive beeps, and exciting lights.

Unitron allows you to convert between common volume units (cups, ounces, tablespoons, teaspoons and milliliters). It can also convert from volume to mass (and vice-versa), taking into account the density of common cooking ingredients. This makes measuring ingredients for volume-based recipes with a kitchen scale a breeze. It also functions as a handy countdown timer!

Watch the demo video [here](https://vimeo.com/719658219).

Unitron was developed by Andy Lustig.

![unitron](docs/unitron_small.jpeg)

![front render](docs/render_front.png)
![back render](docs/render_back.png)
![back real](docs/1_14_apart.jpg)

![unitron](docs/1_14_on.jpg)
![back real](docs/1_14_back.jpeg)

## Build Guide

### BOM

| Qty | Reference     | Description              | Value/MPN                                                                                                                                            |
| --- | ------------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | BT2           | Battery Connector        | [2468](https://www.digikey.com/product-detail/en/keystone-electronics/2466/36-2466-ND/303815)                                                        |
| 1   | C1            | 0805 Capacitor           | 1µF                                                                                                                                                  |
| 1   | C2            | 0805 Capacitor           | 100nF                                                                                                                                                |
| 1   | C3            | 0805 Capacitor           | 10µF                                                                                                                                                 |
| 6   | D1-6          | Addressable RGB LED      | [WS2812B](https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf)                                                                                      |
| 1   | D7            | Diode                    | [SM5817PL-TP](https://www.digikey.com/en/products/detail/micro-commercial-co/SM5817PL-TP/1793251)                                                    |
| 2   | D8, D9        | 0805 Indicator LED       | Red and Yellow                                                                                                                                       |
| 4   | H1-4          | Threaded Standoff        | [4207](https://www.adafruit.com/product/4207)                                                                                                        |
| 2   | J1, J3        | 1x8 male header          | [TSM-108-01-T-SV](https://www.digikey.com/en/products/detail/samtec-inc/TSM-108-01-T-SV/6679033)                                                     |
| 2   | J2, J4        | 1x8 female header        | [SSW-108-01-T-S](https://www.digikey.com/en/products/detail/samtec-inc/SSW-108-01-T-S/1112297)                                                       |
| 1   | LS1           | Buzzer                   | [PK-11N40PQ](https://www.digikey.com/en/products/detail/mallory-sonalert-products-inc/PK-11N40PQ/4996072?s=N4IgTCBcDaICwFYAcBaAjAZjmFA7AJiALoC%2BQA) |
| 21  | R1-18, R22-24 | 0805 Resistor            | 10KΩ                                                                                                                                                 |
| 3   | R19, R20, R21 | 0805 Resistor            | 2KΩ                                                                                                                                                  |
| 14  | S1-14         | Mechanical Key Switch    | [Gateron green](https://www.amazon.com/Gateron-KS-9-Mechanical-Type-Switch/dp/B07X3TH4DS?th=1)                                                       |
| 1   | SW1           | Small Toggle             | [B12AP](https://www.digikey.com/en/products/detail/nkk-switches/B12AP/379099)                                                                        |
| 1   | SW2           | Big Toggle               | [M2012EA2W13](https://www.digikey.com/en/products/detail/nkk-switches/M2012EA2W13/4509655)                                                           |
| 1   | SW3           | Rotary Encoder           | [PEC11R-4215F-S0024](https://www.digikey.com/en/products/detail/bourns-inc/PEC11R-4215F-S0024/4499665)                                               |
| 2   | U1, U2        | Yellow 4-Digit Display   | [LTC-4727JS](https://www.digikey.com/products/en?keywords=LTC-4727JS)                                                                                |
| 2   | U3, U8        | 7-Segment Display Driver | [AS1115-BSST](https://www.digikey.com/products/en?keywords=AS1115-BSSTCT-ND)                                                                         |
| 1   | U4            | QT Py RP2040             | [4900](https://www.adafruit.com/product/4900)                                                                                                        |
| 1   | U5            | Battery Charging IC      | [MCP73831](https://www.digikey.com/en/products/detail/microchip-technology/MCP73831T-2ATI-OT/964303)                                                 |
| 2   | U6, U7        | Red 4-Digit Display      | [LTC-4727JR](https://www.digikey.com/products/en?keywords=160-1551-5-nd)                                                                             |

<div style="">
  <a href="https://alustig3.github.io/unitron/ibom.html">
  <img src="docs/ibom_click.png">
  </a>
</div>

### Additional Components
- A rechargeable 3.7V lithium polymer (LiPo) [battery](https://www.adafruit.com/product/1578)
- Threaded mounting [magnets](https://www.kjmagnetics.com/proddetail.asp?prod=MM-C-10)
- A satisfyingly knurled [metal knob](https://www.digikey.com/en/products/detail/kilo-international/OEDNI-63-4-7/5970335).
- Keycaps from WASD keycaps:
  - [number pad keycap set](https://www.wasdkeyboards.com/17-key-cherry-mx-number-pad-keycap-set.html) for the numbers (black, large font)
  - The number pad set comes with a 1x2 "0" keycap, but we want a [custom 1x1 "0" keycap](https://www.wasdkeyboards.com/custom-text-cherry-mx-keycaps.html) (R1 1x1, 26 font, center-center alignment)
  - [R1 1x1 keycaps](https://www.wasdkeyboards.com/row-1-size-1x1-cherry-mx-keycap.html) (sky blue, green, and orange)
- [Relegendable keycaps](https://www.adafruit.com/product/5039) are a good less expensive alternative.

## User Guide

### <a name="diagram"></a>Component Diagram
![Unitron component diagram](docs/UnitronComponents.png)
### <a name="on"></a>Turning it on!

The first step to using your Unitron is to turn it on with the smaller, right-most [On/Off switch](#diagram). When Unitron is on, the [LED panel](#diagram) and the red [Power indicator light](#diagram) will be lit up. Turn it off to save power.

### Switching Modes

Unitron has a [countdown timer mode](#timer) and [converter mode](#convert).
To **switch to modes**, click the [blue Mode button](#diagram).
Unitron will startup in the `start_mode` specified in your `settings.py` file (see [Modifying Unitron functionality](#modify)).
If the [blue Mode button](#diagram) is pressed down when turning on Unitron, it will startup in the opposite mode. 

### <a name="timer"></a>Countdown timer mode
To **set the timer**, use the number keys. To specify minutes and seconds, you can use the decimal key, e.g. 20.30 corresponds to 20 minutes and 30 seconds, while 20 corresponds to 20 seconds.

To **start** the timer, flip the [Toggle switch](#diagram). To **pause** the timer, flip the [Toggle switch](#diagram) again. The top, red row of the LED panel shows the time remaining, and the bottom orange row shows the original time requested.

To **clear** the timer, pause the timer (if necessary), then push the green [Clear button](#diagram).

As the timer counts down to 0, a bar of [Timer lights](#diagram) will progressively light up. When the timer reaches 0, it will beep three times.

### <a name="convert"></a>Converter mode
Unitron converts **from blinking to solid units** in the [Unit light](#diagram) row.

You can **enter the amount** of the **blinking "from"** units with the number keys. This will be shown in the [LED panel](#diagram). The corresponding amount in the **solid "to"** units will be shown in the other row of the [LED panel](#diagram).

You can **change units** using the [Knob](#diagram). Turning the knob changes the **blinking "from" units**. Turning the knob while holding it down changes the **solid "to" units**.

You can **swap** the "from" and "to" units with the [Toggle switch](#diagram).  If you find it difficult to hold down the Knob while turning it, you can use the Toggle switch to swap, turn the knob, then flip the Toggle switch back.

Conversions between volume and mass require knowing the density of the ingredient. You can **specify cooking ingredients** by holding down the orange [Ingredient button](#diagram) while turning the [Knob](#diagram). Note that the ingredient button only functions when the two units selected are mass and volume -- ingredient type does not matter when converting from mass to mass or volume to volume.

### Charging

Unitron is rechargeable. To charge it, plug a USB C cable into the [USB port](#diagram) at the top. The yellow charging indicator will be on while charging and will turn off when the battery is full.

### Placement

The back of Unitron has four strong magnets. It is meant to be placed on a metallic refrigerator.

### <a name="modify"></a> Modifying Unitron functionality

Unitron uses [CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython). 
You can modify the code it is running by connecting it to your computer via the [USB C port](#diagram) and mounting it as a disk drive.
Basic settings can be adjusted by editing the `settings.py` file.

**Change the mode that Unitron starts up in when turned on** by editing `start_mode`.

**Adjust the number of beeps** for when the timer expires by editing `beep_num`.

To **add new ingredients** to Unitron, modify `ingredients`. Specify the density in grams per teaspoon. You can try to measure these densities yourself, or you can trust the internet. Here's one [site](https://www.howmany.wiki/vw/) with information.

Make sure to **eject** Unitron before disconnecting.

### Updating Software

Connect to Unitron a computer via the [USB C port](#diagram) and mount it as a disk drive.
It should appear as "CIRCUITPY".
Download the latest software [release](https://github.com/alustig3/unitron/releases).
Unzip the download and copy the files onto the "CIRCUITPY" drive.
