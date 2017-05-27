Version 4
SymbolType CELL
LINE Normal -27 -19 -24 -19
LINE Normal -22 -32 -32 -32
LINE Normal -22 32 -32 32
LINE Normal 29 0 32 0
LINE Normal -22 -16 -32 -16
LINE Normal -22 16 -32 16
CIRCLE Normal 29 4 21 -4
ARC Normal -69 -32 21 32 -22 36 -23 -40
ARC Normal -20 -32 -44 32 -32 38 -32 -35
WINDOW 0 11 -32 Left 2
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
