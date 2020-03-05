Version 4
SymbolType CELL
LINE Normal -32 32 32 64
LINE Normal -32 96 32 64
LINE Normal -32 32 -32 96
LINE Normal -28 48 -20 48
LINE Normal -28 80 -20 80
LINE Normal -24 84 -24 76
WINDOW 0 0 32 Left 0
SYMATTR Prefix X
SYMATTR Description Ideal single-pole operational amplifier. You must .lib opamp.sub
SYMATTR Value opamp
SYMATTR SpiceLine Aol=100K
SYMATTR SpiceLine2 GBW=10Meg
PIN -32 48 NONE 0
PINATTR PinName invin
PINATTR SpiceOrder 1
PIN -32 80 NONE 0
PINATTR PinName noninvin
PINATTR SpiceOrder 2
PIN 32 64 NONE 0
PINATTR PinName out
PINATTR SpiceOrder 3
