Version 4
SymbolType CELL
LINE Normal -32 -17 -24 -17
LINE Normal -32 15 -24 15
LINE Normal -28 19 -28 11
LINE Normal -44 -16 -48 -16
LINE Normal -44 16 -48 16
LINE Normal 44 0 48 0
LINE Normal -13 -41 -24 -49
LINE Normal -24 -33 -13 -41
LINE Normal -24 -49 -24 -33
RECTANGLE Normal 44 57 -44 -57
CIRCLE Normal 14 -38 4 -44
CIRCLE Normal 24 -38 14 -44
WINDOW 0 -31 -70 Left 2
SYMATTR SpiceModel level.2
SYMATTR Prefix X
SYMATTR Description Universal Opamp model that allows 4 different levels of simulation accuracy.  See ./examples/Educational/UniversalOpamp2.asc for details.  En and in are equivalent voltage and current noises.  Enk and ink are the respective corner frequencies.  Phimargin is used to set the 2nd pole or delay to the approximate phase margin for level.3a and level.3b.  This version uses the new, experimental level 2 switch as the output devices.
SYMATTR Value2 Avol=1Meg GBW=10Meg Slew=10Meg
SYMATTR SpiceLine ilimit=25m rail=0 Vos=0 phimargin=45
SYMATTR SpiceLine2 en=0 enk=0 in=0 ink=0 Rin=500Meg
SYMATTR ModelFile UniversalOpamps2.sub
PIN -48 16 NONE 0
PINATTR PinName In+
PINATTR SpiceOrder 1
PIN -48 -16 NONE 0
PINATTR PinName In-
PINATTR SpiceOrder 2
PIN 48 0 NONE 0
PINATTR PinName OUT
PINATTR SpiceOrder 5
