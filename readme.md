# Unitron
![unitron](docs/unitron_small.jpeg)

![front render](docs/render_front.png)
![back render](docs/render_back.png)

![back real](docs/1_14_apart.jpg)
![unitron](docs/1_14_on.jpg)
![back real](docs/1_14_back.jpeg)


## BOM

| Qty | Reference                                                                                      | Description              | Value/MPN                                                                                                                                            | 
|-----|------------------------------------------------------------------------------------------------|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | BT2                                                                                            | Battery Connector        | [2468](https://www.digikey.com/product-detail/en/keystone-electronics/2466/36-2466-ND/303815)                                                        | 
| 1   | C1                                                                                             | 0805 Capacitor           | 1µF                                                                                                                                                  | 
| 1   | C2                                                                                             | 0805 Capacitor           | 100nF                                                                                                                                                | 
| 1   | C3                                                                                             | 0805 Capacitor           | 10µF                                                                                                                                                 | 
| 6   | D1, D2, D3, D4, D5, D6                                                                         | Addressable RGB LED      | [WS2812B](https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf)                                                                                      | 
| 1   | D7                                                                                             | Diode                    | [SM5817PL-TP](https://www.digikey.com/en/products/detail/micro-commercial-co/SM5817PL-TP/1793251)                                                    | 
| 2   | D8, D9                                                                                         | 0805 Indicator LED       | Red and Yellow                                                                                                                                       | 
| 4   | H1, H2, H3, H4                                                                                 | Threaded Standoff        | [4207](https://www.adafruit.com/product/4207)                                                                                                        | 
| 2   | J1, J3                                                                                         | 1x8 male header          | [TSM-108-01-T-SV](https://www.digikey.com/en/products/detail/samtec-inc/TSM-108-01-T-SV/6679033)                                                     | 
| 2   | J2, J4                                                                                         | 1x8 female header        | [SSW-108-01-T-S](https://www.digikey.com/en/products/detail/samtec-inc/SSW-108-01-T-S/1112297)                                                       | 
| 1   | LS1                                                                                            | Buzzer                   | [PK-11N40PQ](https://www.digikey.com/en/products/detail/mallory-sonalert-products-inc/PK-11N40PQ/4996072?s=N4IgTCBcDaICwFYAcBaAjAZjmFA7AJiALoC%2BQA) | 
| 21  | R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R15, R16, R17, R18, R22, R23, R24 | 0805 Resistor            | 10KΩ                                                                                                                                                 | 
| 3   | R19, R20, R21                                                                                  | 0805 Resistor            | 2KΩ                                                                                                                                                  | 
| 14  | S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14                                    | Mechanical Key Switch    | [Gateron green](https://www.amazon.com/Gateron-KS-9-Mechanical-Type-Switch/dp/B07X3TH4DS?th=1)                                                       | 
| 1   | SW1                                                                                            | Small Toggle             | [B12AP](https://www.digikey.com/en/products/detail/nkk-switches/B12AP/379099)                                                                        | 
| 1   | SW2                                                                                            | Big Toggle               | [M2012EA2W13](https://www.digikey.com/en/products/detail/nkk-switches/M2012EA2W13/4509655)                                                           | 
| 1   | SW3                                                                                            | Rotary Encoder           | [PEC11R-4215F-S0024](https://www.digikey.com/en/products/detail/bourns-inc/PEC11R-4215F-S0024/4499665)                                               | 
| 2   | U1, U2                                                                                         | Yellow 4-Digit Display   | [LTC-4727JS](https://www.digikey.com/products/en?keywords=LTC-4727JS)                                                                                | 
| 2   | U3, U8                                                                                         | 7-Segment Display Driver | [AS1115-BSST](https://www.digikey.com/products/en?keywords=AS1115-BSSTCT-ND)                                                                         | 
| 1   | U4                                                                                             | QT Py RP2040             | [4900](https://www.adafruit.com/product/4900)                                                                                                        | 
| 1   | U5                                                                                             | Battery Charging IC      | [MCP73831](https://www.digikey.com/en/products/detail/microchip-technology/MCP73831T-2ATI-OT/964303)                                                 | 
| 2   | U6, U7                                                                                         | Red 4-Digit Display      | [LTC-4727JR](https://www.digikey.com/products/en?keywords=160-1551-5-nd)                                                                             | 


<div style="">
  <a href="https://alustig3.github.io/unitron/ibom.html">
  <img src="docs/ibom_click.png">
  </a>
</div>

### Keycaps
Keycaps were bought from WASD Keyboards.
- [number pad keycap set](https://www.wasdkeyboards.com/17-key-cherry-mx-number-pad-keycap-set.html) for the numbers (black, large font)
- The number pad set comes with a 1x2 "0" keycap, but we want a [custom 1x1 "0" keycap](https://www.wasdkeyboards.com/custom-text-cherry-mx-keycaps.html) (R1 1x1, 26 font, center-center alignment)
- [R1 1x1 keycaps](https://www.wasdkeyboards.com/row-1-size-1x1-cherry-mx-keycap.html) (sky blue, green, and orange)

[Relegendable keycaps](https://www.adafruit.com/product/5039) could be used as a less expensive option.

## User Guide