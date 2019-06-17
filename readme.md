# LT2circuiTikz conversion script

## What this script does
This script takes a [LTSpice](http://www.linear.com/solutions/ltspice) (IV, XVII) circuit file (*.asc) and tries to convert it to a  [LaTeX](https://www.latex-project.org/get/) document containing a [pgf/TikZ](https://www.ctan.org/pkg/pgf) picture of the schematic, using the [CircuiTikZ](https://www.ctan.org/pkg/circuitikz) package to draw the symbols.
The document can then be compiled, e.g. into PDF format.

Take a look at this [example PDF file](https://github.com/ckuhlmann/lt2circuitikz/blob/master/examples/catalog.asc.pdf) produced from [this](https://github.com/ckuhlmann/lt2circuitikz/blob/master/examples/catalog.asc) sample document [(direct comparison)](https://github.com/ckuhlmann/lt2circuitikz/blob/master/examples/catalog.png).


Currently supported features:

 * Wires with automatic junction creation
 * Text nodes (with support for font-size selection) and Net Labels (with automatic GND conversion).
 * Graphic elements (lines, rectangles) with line-style support
 * Basic schematic LTSpice library elements (R, L, C, Sources, Transistors, Opamp)
 * Almost the complete CircuiTikZ symbol library (as of 2017-05) is available as LTSpice symbols. Many come with different style options to choose from. Where possible, these symbols have been derived using the native Spice elements, which means that circuits drawn with these symbols also work for simulations. This might require adding/specifying device models in a similar way as it is required for the generic symbols from Linear.
 * New symbols can be added by creating them in LTSpice and a simple *.asy2tex ASCII file with instructions how to represent that symbol as TeX commands.

## Requirements

1. [LTSpice](http://www.linear.com/solutions/ltspice) (IV, XVII) circuit file (*.asc)
2. [Python 3.4+](https://www.python.org/downloads/release/python-344/) or Windows system when using precompiled executable. (3.4 is currently the latest python version that works with [py2exe](www.py2exe.org/), in case you want to build your own executable).
3. Copies of the symbol files (*.asy) of all used circuit elements in the sym32a subfolder of the script at the same relative path as they are in your LTSpice library 
   * To use the supplied library, copy the `sym32a\circuiTikz` directory to your LTSpice library sym directory (`C:\Users\[username]\Documents\LTspiceXVII\lib\sym` on Windows with version XVII, or `[LTSpiceIVInstallDir]\lib\sym` for version IV). You don't need to copy the *.asy2tex files, but LTSpice is smart enough to ignore them if you do so. 
   * The `circuiTikz` folder in your LTspice lib directory should be at `lib\circuiTikz`. Do _not_ copy the `sym32a` folder itself to `lib`, only its `circuiTikz` subdirectory! 
   
4. Conversion files *.asy2tex with the same name as the symbol. Symbol files and conversion files for many circuit elements are packaged with the script.
5. LaTeX with the standalone, circuitikz, tikz, pgfplots, packages installed. The default preamble also requires amsmath, amssymb,bm,color,pgfkeys,siunitx,ifthen,ulem, but you might be able to get along without them by removing the \\usepackage lines.


## Usage

To convert a file just call lt2ti.py with the full path to the *.asc file you want to convert as argument. E.g. if you want to convert the file D:\\testdrive\\catalog.asc, with the script in D:\\scriptdir\\LT2circuiTikz\\ run
```bash
python "D:\scriptdir\LT2circuiTikz\lt2ti.py" "D:\testdrive\catalog.asc">run.log
```
or, when using the executable
```bash
"D:\scriptdir\LT2circuiTikz\lt2ti.exe" "D:\testdrive\catalog.asc">run.log
```

You will then find your converted file at D:\\testdrive\\catalog.asc.tex

Compile this file with pdflatex
```bash
pdflatex "D:\testdrive\catalog.asc.tex"
```

to finally get a PDF document  D:\\testdrive\\catalog.asc.pdf with your shematic.

Please note that you might want to change the extension to a simple .pdf in order to not confuse LaTeX when then using the PDF in another LaTeX document.

## Testrun
Use the supplied `test_lt2ti.bat` file to test your python setup with lt2ti.py on an example file. 

Use `examples\compile_catalog.bat` to compile a pdf from the catalog example file to test your latex setup. 

The expected outputs are present in the package (and get overwritten, so create copies if you want to compare the results. Alternatively, use git to diff for deviations).

## Scripting

If you want to automate this script even further, you can use it as a python module:
```python
import lt2ti;
fn = r'examples\catalog.asc';
l2tobj = lt2ti.lt2circuiTikz();
l2tobj.readASCFile(fn);
l2tobj.writeCircuiTikz(fn+r'.tex');
```


## Why you might want to use this script

If you want to quickly create large, professional looking, publication ready schematics, this script will vastly reduce the time required to get you there. 

## Limitations

If you are already familiar with CircuiTikZ and write large schematics using it with ease, this script will only complicate your workflow. However, when you already use LTSpice for simulations, you might at least want to try it.

As with most automatically generated code, the output of the script is not as nicely formatted and structured as the result coming from a skilled human. More precisely, it uses absolute coordinates and it groups circuit elements by type and not by semantics. This means that you will find the wires of a voltage divider in a different part of the document than the resistors. The visual result is the same, but the LaTeX code structure could be improved.

Due to the limited graphical capabilities of LTSpice schematic capture (which aims at simulation, not publication), there are limits of what can be achieved without editing the LaTeX output. Especially the grid of LTSpice is rather rough and therefore limits component placement but helps to achieve consistent looking schematics.

It also requires the use of non-free (as in freedom) software if that's an issue for you. Since IMHO LTSpice is one of the best free (as in beer) simulators around, this is unlikely to change in the future.
It also has a very easy to parse, yet astonishingly powerful file format for symbols and schematics, which was the reason for choosing it as schematic entry.

## Legal

Trademark and copyright notice:
LTspice is a registered trademarks of Linear Technology Corporation, now part of Analog Devices, Inc.
This script or its author are not in any way affiliated to these companies.

This script is provided as-is and without any warranty.

## Customization

 * You can adjust the default styles (e.g. to use american symbols) by editing the preamble files (e.g. `sym32a\latex_preamble.tex`, `sym32a\latex_closing.tex`). The file `sym32a\latex_ext.tex` is meant to be used to add additional CircuiTikZ symbols or to patch existing ones.
 * The default Ground symbol is defined in the sym.ini file under `[general]` with the entry `default_gnd=circuiTikz\gnd`. Replace the string right to the = sign with the path and name of the .asy2tex gnd symbol file you want to use (without the extension), e.g. `circuiTikz\ground`.
 * Further customizations are possible by editing the .asy2tex files, see the Creating new symbols section below.

## Creating new symbols

### Adding symbols to LTspice
Creating new symbols in LTspice works the same way as it does normally (see the _Creating New Symbols_ section in the LTspice help file). 
There are no required extra steps involved. To have good visual equivalence between the spice circuit and the circuiTikz result, your pin spacing and proportions in your spice symbol compared to existing symbols should approximately match the ratio of the two circuiTikz symbols. To make debugging easier, you could try to position your origin at the center or at a pin, but this is not mandatory. Please consult one of the many good tutorials on how to create symbols in LTspice on how to do this. If you only use the new symbol to create circuiTikz graphics, you don't need to provide a valid spice model. If you want to be able to simulate the circuit as well, you should provide one.

### Creating an asy2tex file to translate a (new) LTspice symbol to CircuiTikZ
asy2tex files are the ones that store information on how to convert any symbol found in the schematic to circuiTikZ code.
To add a new symbol you need to do the following:
1. Copy the new spice symbol (asy file) for which you want to add lt2circuitikz support into the lt2circuitikz sym folder you are using, usually `sym32a`. The relative location of the symbol file in the sym folder needs to be the same as in the LTspice sym folder. I.e., if your symbol resides in `sym\someFolder\newSymbol.asy` in your LTspice lib, you need to place it e.g. at `sym32\someFolder\newSymbol.asy`. lt2circuitikz needs the symbol to look up the pin names and positions.
2. Create a new asy2tex file that has the same name as the asy file, just with the asy2tex extension in the same folder. E.g. if you copied `MyNewSymbol.asy` to `sym32a\someFolder\`, you need to create a `MyNewSymbol.asy2tex` text file in the same directory (thus at `sym32a\someFolder\MyNewSymbol.asy2tex`). This is a plain ascii text file.
3. Open the asy2tex file and enter the required tokens according to the [following section](#asy2texdocu) to produce the desired circuiTikz code. Use existing conversion files as a template.
	* The general outline should be (<> mark places where you enter data):
		```
		Type <SymbolTypeHere>
		TexOrigin <x y rot mirror>
		SymOrigin <x y rot mirror>
		BeginPinList
		EndPinList
		TexElementName <texElementName>
		BeginTex
		 <CircuiTikzCodeToCreateSymbol>
		EndTex
		```
		There are also more advanced fields available, [see below](#asy2texdocu).
	* To get you started, first look up the symbol in the circuiTikz manual and see whether it is a bipole, tripole or some other symbol (e.g. an opamp). Choose the [Type](#ElemType) in the asy2tex file accordingly.
	* Take a look at the existing asy2tex file of the same type to get you started and with a template.
	* Bipoles are often very straight forward: Simply replace the element name of an existing element (e.g. a resistor) and most of the time you are done. 
	They usually contain the bipole element and reference the translated coordinates of the symbol pins via [#&lt;PinName&gt;:x1#](#ElemPinNamex1) and [#&lt;PinName&gt;:x1#](##ElemPinNamey1), where &lt;PinName&gt; is the name of the pin in the spice symbol.
	* Opamp and transistor symbols often come down to positioning the circuiTikz symbol, so that the pins get positioned on the LTspice grid as transformed to the circuiTikz plane. Insert the symbol at [#self.texx1#, #self.texy1#](#ElemSelftexx1Selftexx2). Use the [SymOrigin](#ElemSymOrigin) field to move the symbol around in the spice domain, in order to map your spice origin to the circuiTikz symbol origin. Similarly, [TexOrigin](#ElemTexOrigin) moves the origin in the latex coordinate space. Having the origin at the center is a huge benefit for complex symbols (in both domains). For most symbols, moving the origin to the proper place will align the pins at the same time.
	* If the circuiTikz pins are not on-grid because the distance between them does not match the spice grid (in the circuiTikz plane), you need to scale the symbol. Take a look at the sym32b\latex_preamble.tex preamble file to see how scaling can be done in circuiTikz. However, it is generally advisable to use the same grid for new circuiTikz symbols as that of the existing ones, and therefore scaling should not be necessary for sym32a style conversions (see below what sym32a, sym32b means). All currently translated circuiTikz symbols have this grid pattern.
	You might need to add short wires to connect to the "spice" pins. See the opamp symbols' `UniversalOpamp2.asy2tex` as examples. It creates a named node by using the [#self.name#](#ElemSelfName) token and thus allows a unique reference to its pins. You can also use the capability to specify relative coordinates in circuiTikz to your advantage, e.g. when positioning labels.
4. Give the new symbol a try by using it in a schematic (*.asc) file, convert it like described previously, and compile the latex file to check the result. Adjust the asy2tex code until the result pleases you. Congratulations, you have just created your first lt2circuitikz symbol!

<a name="asy2texdocu"></a>
### \*.asy2tex file documentation 

asy2tex files perform the conversion from *.asy symbols to LaTeX commands.
A typical asy2tex file looks like this:
```tex
Type Node
TexOrigin 0 0 0 False
SymOrigin 2.836 0 0 False
BeginPinList
EndPinList
TexElementName op amp
BeginTex
 \draw (#self.texx1#, #self.texy1#) node[#self.symbol.latexElementName#, xscale=##mirror_xscale_value##, rotate=##rotate##, ##options##] (#self.name#) {}  (#self.name#)++(##labelmirrorx##*0.75,  ##labelmirrory##*1.25) node {#self.name# #self.value#};
 \draw (#V+:x1#,#V+:y1#) to [*short, -] (#self.name#.up);   \draw (#V-:x1#,#V-:y1#) to [*short, -] (#self.name#.down); % supply
 \draw (#In+:x1#,#In+:y1#) to [*short, -] (#self.name#.+);   \draw (#In-:x1#,#In-:y1#) to [*short, -] (#self.name#.-); \draw (#OUT:x1#,#OUT:y1#) to [*short, -] (#self.name#.out); % in/out
EndTex
```
and contains the following elements:
<dl>
<dt><code>ALIASFOR ..\res.asy2tex</code></dt>
<dd>Alias definition. Must be on the first line if present. The file will not be read any further after this line. Instead, the specified translation file will be used as if their contents were copied to this file. Useful if you want to create a new symbol (e.g. a with a defined model etc.) with the same output as an existing one.</dd>

  <dt><a name="ElemType"></a><code>Type</code></dt>
  <dd>Type of the symbol. Can be one of [Node|Bipole|Tripole|&lt;N&gt;pole|Graphical]. Historically, Node can also be used for Tripoles and N-Poles</dd>
  
  <dt><a name="ElemTexOrigin"></a><code>TexOrigin x1 y1 rotatedeg mirror</code></dt>
  <dd>Used to specify an offset (by x1, y1), rotation (in degrees, ccw) and mirroring (True|False) in the LaTeX coordinate system that is applied on top to any shifts to origin specified by the SymOrigin, or the origin of the component on the schematic.</dd>
  
  <dt><a name="ElemSymOrigin"></a><code>SymOrigin x1 y1 rotatedeg mirror</code></dt>
  <dd>Used to specify an offset (by x1, y1), rotation (in degrees, cw) and mirroring (True|False) in the Spice schematic coordinate system that is applied on top to any shifts to origin specified by the origin of the component on the schematic</dd>

  <dt><code>BeginPinList</code></dt>
  <dd>Marks the beginning of the pin list</dd>
  
   <dt><code>PinNum x1 y1 rot length PinName</code> (not shown)</dt>
  <dd>Pin-list entry. Manually defines a pin in the LaTeX coordinate space at (x1,y1) with the defined rotation, lengh and pin-name. Currently not in use since the pins of all symbols come from their symbol files.</dd> 
  
  <dt><code>EndPinList</code></dt>
  <dd>Marks the end of the pin list</dd>
  
  <dt><code>BeginConversionKeyvals</code></dt>
  <dd>Marks start of conversion key=value list</dd>
  
  <dt><code>key=val</code></dt>
  <dd>entry of the conversion key-val list</dd>
  
  <dt><code>EndConversionKeyvals</code></dt>
  <dd>Marks end of conversion key=value list</dd>
  
  
  <dt><code>TexElementName texname</code></dt>
  <dd>Specifies the LaTeX name of the symbol as texname, for later use with placeholders</dd>
  
  <dt><code>BeginTex</code></dt>
  <dd>Marks the beginning of the tex command section</dd>
  
  <dt><code>LaTeX code</code></dt>
  <dd>These are the command that produce the component in the LaTeX document. In order to position it correctly, some placeholders can be used to insert values and coordinates:
  <dl>
  
  <dt><a name="ElemSelftexx1Selftexx2"></a><code>#self.texx1#</code>, <code>#self.texy1#</code></dt>
  <dd>Returns the x- or y-coordinate (in LaTeX space) of the component origin</dd>
  
  <dt><a name="ElemPinNamex1"></a><code>#PinName:x1#</code></dt>
  <dd>Returns the x-coordinate (in LaTeX space) of the pin named PinName (in the asy-file)</dd>
  
  <dt><a name="ElemPinNamey1"></a><code>#PinName:y1#</code></dt>
  <dd>Returns the y-coordinate (in LaTeX space) of the pin named PinName (in the asy-file)</dd>
  
  <dt><code>#PinName:junction#</code></dt>
  <dd>Returns a * if the pin named PinName (in the asy-file) is at a junction point, returns an empty string otherwise. Useful for bipoles and wires.</dd>
  
  <dt><code>#self.symbol.latexElementName#</code></dt>
  <dd>Returns the name specified under TexElementName</dd>
  
  <dt><a name="ElemSelfName"></a><code>#self.name#</code></dt>
  <dd>The designator on the schematic for this component.</dd>
  
  <dt><code>#self.value#</code></dt>
  <dd>The value on the schematic for this component.</dd>
  
  <dt><code>#self.value2#</code> or <code>##options##</code></dt>
  <dd>The value2 on the schematic for this component. Also use to supply tex-options. Unfortunately, this often prevents a schematic from simulating correctly, but there are no comment fields available on component instances.</dd>
  
  <dt><code>##rotate##</code></dt>
  <dd>The amount of ccw rotation (in degrees).</dd>
  
  <dt><code>##mirror_invert##</code>, <code>##mirror_mirror##</code>, <code>##mirror_xscale##</code></dt>
  <dd>return the strings invert, mirror or xscale=-1 if the component is mirrored on the schematic. Return empty strings if not.</dd>
  
  <dt><code>##mirror_xscale_value##</code>, <code>##mirror_yscale_value##</code></dt>
  <dd>Return -1 if the component is mirrored, returns 1 otherwise.</dd>
  
   <dt><code>##mirror_rot_xscale_value##</code></dt>
   <dd>Returns -1 if the component is mirrored <i>and <b>not</b></i> rotated by multiples of 90 degrees. Returns 1 for all other cases. Useful for handling mirrored placement of OpAmp and transistor labels.</dd>
     
  <dt><code>##mirror_rot_yscale_value##</code></dt>
  <dd>Returns -1 if the component is mirrored <i>and</i> rotated by multiples of 90 degrees. Returns 1 for all other cases. Useful for handling mirrored placement of OpAmp and transistor labels.</dd>
  
  <dt><code>##rotate_&lt;num&gt;_pmvalue##</code></dt>
  <dd>Returns 1 if the component is rotated by num degrees or odd multiples of it. Returns -1 otherwise. Enter num without &lt;&gt;.</dd>
  
  <dt><code>##rotate_&lt;num&gt;_mpvalue##</code></dt>
  <dd>Returns -1 if the component is rotated by num degrees or odd multiples of it. Returns 1 otherwise. Enter num without &lt;&gt;.</dd>
  
  <dt><code>##rotate_&lt;num&gt;_10value##</code></dt>
  <dd>Returns 1 if the component is rotated by num degrees or odd multiples of it. Returns 0 otherwise. Enter num without &lt;&gt;.</dd>
  
  <dt><code>##rotate_&lt;num&gt;_01value##</code></dt>
  <dd>Returns 0 if the component is rotated by num degrees or odd multiples of it. Returns 1 otherwise. Enter num without &lt;&gt;.</dd>
  
  <dt><code>##labelmirror&lt;x|y&gt;##</code></dt>
  <dd>x: Returns -1 if the component (is not rotated and mirrored) or (is 180 degrees rotated and not mirrored). Returns 1 otherwise.<br>
  y: Returns -1 if the component (is rotated by 90 degrees) or (is rotated by -270 degrees). Returns 1 otherwise.<br>enter x or y without &lt;&gt; and |
  </dd>
  
  
  <dt><code>#self.&lt;attrib&gt;#</code></dt>
  <dd>Returns the value of the attribute attrib from the internal component object. Enter name without &lt;&gt;.</dd>
  
  <dt><code>#self.symbol.&lt;attrib&gt;#</code></dt>
  <dd>Returns the value of the attribute attrib from the internal symbol object. Enter name without &lt;&gt;.</dd>
  
  <dt><code>#self.symbol.conversionKV.&lt;key&gt;#</code></dt>
  <dd>Returns the value of key from the ConversionKeyvals list. Enter name without &lt;&gt;.</dd>
  

  </dl>
  </dd>
  
  <dt><code>EndTex</code></dt>
  <dd>Marks the end of the tex command section</dd>
</dl>


The most common components have already been translated and reside in the sym* folders. You can tweak them as you like to produce the output you desire.
 *  the sym32a folder is the preferred translation style and contains the largest symbol collection. It produces nice coordinates but uses a scale of 0.666666 to achieve pleasant optics. With this style, nmos, pmos transistors are shifted so that the gate pin lies on the schematic grid.
 * the sym32b folder uses the same nice coordinates and a scale of 0.66666, but scales the nmos, pmos transistors so that their gate become on-grid. For consistency, pnp, npn transistors are scaled in the same way. Therefore the transistors in this style appear a bit large compared to resistors and other bipoles. Use this style if you like to avoid shifted transistors. You may copy many missing symbols from the sym32a style as you see fit. Do not forget to adapt the transistors.
 * the sym48 folder uses all components as close to their default sizes as possible. Unfortunately, this means that many coordinates become 1/3 or 1/6 so that they are rather ugly. Transistors are shifted to make their gates on-grid. This style is visually very close to sym32a, but produces ugly coordinates. On the other hand, it doesn't need a scale value other than 1. It is considered legacy and is not maintained any more.
 