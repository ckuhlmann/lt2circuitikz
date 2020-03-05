Version 4
SymbolType CELL
LINE Normal -32 -32 32 0
LINE Normal -32 32 32 0
LINE Normal -32 -32 -32 32
LINE Normal -28 -16 -25 -16
WINDOW 0 0 -32 Left 2
SYMATTR Prefix X
SYMATTR Description Ideal single-pole operational amplifier. You must .lib opamp.sub
SYMATTR Value opamp
SYMATTR SpiceLine Aol=100K
SYMATTR SpiceLine2 GBW=10Meg
PIN -32 -16 NONE 0
PINATTR PinName invin
PINATTR SpiceOrder 1
PIN -32 16 NONE 0
PINATTR PinName noninvin
PINATTR SpiceOrder 2
PIN 32 0 NONE 0
PINATTR PinName out
PINATTR SpiceOrder 3
