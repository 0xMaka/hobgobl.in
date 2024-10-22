title : Scrap  Cooler (for Ethereum NUC Node)
notes : A custom cooler for an Ethereum NUC node.
image : scrap_cooler.png
repo  : https://github.com/0xmaka/scrap_cooler
order : 4

Housed in the repurposed shell of a Corsair CX500M power supply, this _scrap cooler_ uses an old 4 pin PC fan driven at 12 volts via a voltage booster,
controlled by PWM from a Pico driven at 3.3 volts.
<br><br>
Feedback is given through a 2 line LCD, driven at 5 volts, connected via a bidirectional logic-level shifter for reliable communication with the MCU.
The build uses a thermistor to take temperature readings of the enclosure, and features 3 speeds selected via a push button.