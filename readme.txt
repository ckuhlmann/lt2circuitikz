This is lt2circuitTikz.

It reads the schematic files produced by LTspice (R) and converts them into a latex graphic using pgfplot,tikz and circuitikz.
These graphics can then be compiled using pdflatex into pdf format.

This translation process requires the following (in addition to python 3.5+)
	1) an input *.asc schematic of version 4 (LTspice IV and XVII)
	2) for every schematic component, the corresponding *.asy symbol file, copied to the sym32a subdirectory
	     if the symbol is not in the LTspice library root folder, the symbol must be copied to a subfolder structure with the same relative path as the symbol file in the library directory.
	     e.g.: a symbol  somecomponent.asy is located in lib\sym\some\folder\somecomponent.asy, then it should be copied to sym32a\some\folder\somecomponent.asy
	3) for every symbol, a translation file *.asy2tex with the same name as the *.asc file at the same location within the sym32a\ folder.
	     This file specifies the circuiTikz command that is used to generate the component in the latex document.
	     
	and is achieved by calling
	python lt2ti.py schematicfile.asc
	     
	lt2circuiTikz will use the component name and value from the .asc schematic, as well as the pin names and locations from the .asy symbol file and make this information available 
	in the .asy2tex translation file.
	Component names can be accessed using the #self.name# placeholder, #self.value# is replaced with the value. The value2 field can be used to specify additional options and becomes available using ##options## (note the two #).
	The coordinates of component pins (translated into the latex dimensions) are accessed through #PinName:x1# for the x component and #PinName:y1# for the y component of a pin coordinate.
	The origin of the symbol as specified by the schematic (again, translated into tex coordinates) is accessible through #self.texx1#, #self.texy1#.
	
	The entry 
	TexElementName atexname
	is available through #self.symbol.latexElementName#.
	
	TexOrigin x1 y1 rot mirror
	and
	SymOrigin x1 y1 rot mirror
	specify a shift (and rotation/mirror operation) of the origin.
	SymOrigin is in the asc file coordinate system and can be used for symbols where the origin is not at the center.
	TexOrigin is the same but in latex coordinates, so it is rarely of use.
	
	mirroring and rotation can be accessed through 
	##rotate##
	and 
	##mirror##
	the former returns the rotation in degrees (including origin rotation), the ladder the 'mirror' command in case the component is mirrored in the schematic.
	
	##mirror_xscale##
	and
    ##mirror_yscale##
    return xscale=-1 and yscale=-1 respectively in case a component is mirrored in the schematic. If not, the results are empty. If the origin was already mirrored, the results are inversed.
    ##mirror_xscale_value##
    and
    ##mirror_yscale_value##
    just return the value (-1: mirrored, 1: not mirrored), for components where the xscale/yscale should be multiplied with another value.
    
    ##mirror_rot_xscale_value##
    and
    ##mirror_rot_yscale_value##
    alternate x and y mirroring when the component is rotated by 90 degrees, which is neccessary for asymmetric components such as transistors.
    
    It should be noted that the pin locations (#pinName:x1|y1#) are already reported at their mirrored and rotated positions according to the state in the schematic, so no translation for pin positions is necessary
    
    
    The most common components have already been translated and reside in the sym* folders.
      the sym32a folder is the preferred translation style. It produces nice coordinates but uses a scale of 0.666666 to achieve pleasant optics. With this style, nmos, pmos transistors are shifted so that the gate pin lies on the schematic grid.
      the sym32b folder uses the same nice coordinates and a scale of 0.66666, but scales the nmos, pmos transistors so that their gate become on-grid. For consistency, pnp, npn transistors are scaled in the same way. Therefore the transistors in this style appear a bit large compared to resistors and other bipoles.
      the sym48 folder uses all components as close to their default sizes as possible. Unfortunately, this means that many coordinates become 1/3 or 1/6 so that they are rather ugly. Transistors are shifted to make their gates on-grid. This style is visually very close to sym32a, but produces ugly coordinates. On the other hand, it doesn't need a scale value other than 1.
      
      
      
Trademark and copyright notice:
LTspice is a registered trademarks of Linear Technology Corporation, now part of Analog Devices, Inc.
This script or its author are not in any way related to these companies.

This script is provided as-is and without any warranty.