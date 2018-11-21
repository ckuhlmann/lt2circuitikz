import uuid;
import re;
import math;
import copy;
import os;
import configparser;

class lt2circuiTikz:
    
    lastASCfile = None;
    
    reIsHdr = re.compile(r'[\s]*Version 4[\s]+', flags=re.IGNORECASE);
    
    reIsSym = re.compile(r'[\s]*SymbolType[\s]+(.*)$', flags=re.IGNORECASE);# ASY file symbol type definition  do NOT confuse with reIsComponent: an instance of a symbol
    
    reIsSheet = re.compile(r'^[\s]*SHEET[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)', flags=re.IGNORECASE);
    # SHEET                                    no           wx1         wy1
    
    reIsWire = re.compile(r'^[\s]*WIRE[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)', flags=re.IGNORECASE);
    # WIRE                                  x1            y1        x2            y2
    
    reIsNetLabel = re.compile(r'^[\s]*FLAG[\s]+([-\d]+)[\s]+([-\d]+)[\s]+(.*)', flags=re.IGNORECASE);
    # FLAG x1 y1 label
    
    reIsComponent = re.compile(r'^[\s]*SYMBOL[\s]+([\S]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([R|M])([-\d]+)', flags=re.IGNORECASE);
    # SYMBOL path\\type x1 x2 [R|M] rotation
    
    reIsCAttrName = re.compile(r'^[\s]*SYMATTR[\s]+InstName[\s]+(.*)', flags=re.IGNORECASE);
    # SYMATTR InstName name
    
    reIsCAttrValue = re.compile(r'^[\s]*SYMATTR[\s]+Value[\s]+(.*)', flags=re.IGNORECASE);
    # SYMATTR Value value    
       
    reIsCAttrValue2 = re.compile(r'^[\s]*SYMATTR[\s]+Value2[\s]+(.*)', flags=re.IGNORECASE);
    # SYMATTR Value2 value        
    
    reIsCAttrGeneric = re.compile(r'^[\s]*SYMATTR[\s]+([\S]+)[\s]+(.*)', flags=re.IGNORECASE);
    # SYMATTR attr.name value            
    
    reIsWindow = re.compile(r'^[\s]*WINDOW[\s]+([-\d]+)[\s]+([-\d]+)[\s]([-\d]+)[\s]+([\S]+)[\s]+([-\d]+)', flags=re.IGNORECASE);
    # WINDOW                                  attr.No.Id   rel.x1     rel y1       pos.str.    size?=2
    
    reIsText = re.compile(r'^[\s]*TEXT[\s]+([-\d]+)[\s]+([-\d]+)[\s]([\S]+)[\s]+([-\d]+)[\s]+[;!](.*)', flags=re.IGNORECASE);
    # TEXT                                   x1          y1       pos.str.    size?=2         string
    
    reIsLine = re.compile(r'^[\s]*LINE[\s]+([\S]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]*([-\d]*)', flags=re.IGNORECASE);
    # Line                                  type           x1          y1          x2           y2           stype
    
    reIsRect = re.compile(r'^[\s]*RECTANGLE[\s]+([\S]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]*([-\d]*)', flags=re.IGNORECASE);
    # Rect                                       type           x1          y1          x2           y2           stype    
    
    reIsCircle = re.compile(r'^[\s]*CIRCLE[\s]+([\S]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]*([-\d]*)', flags=re.IGNORECASE);
    # Circle/Oval                                type           x1          y1          x2           y2           stype        
    
    
    # symbols:
    
    reIsPin = re.compile(r'^[\s]*PIN[\s]+([-\d]+)[\s]+([-\d]+)[\s]([\S]+)[\s]+([-\d]+)', flags=re.IGNORECASE);
    # PIN                                   x1          y1       pos.str.    offset        
    
    reIsPinName = re.compile(r'^[\s]*PINATTR[\s]+PinName[\s]+(.*)', flags=re.IGNORECASE);
    # PIN PinName                                           pin label
    
    reIsPinOrder = re.compile(r'^[\s]*PINATTR[\s]+SpiceOrder[\s]+([-\d]+)', flags=re.IGNORECASE);
    # PIN PinName                                           pin order    
    
    reIsSAttrValue = re.compile(r'^[\s]*SYMATTR[\s]+Value[\s]+(.*)', flags=re.IGNORECASE);
    # SYMATTR Value value    
    
    reIsSAttrPrefix = re.compile(r'^[\s]*SYMATTR[\s]+Prefix[\s]+(.*)', flags=re.IGNORECASE);
    # SYMATTR Prefix value    
    
    reIsSAttrDescr = re.compile(r'^[\s]*SYMATTR[\s]+Description[\s]+(.*)', flags=re.IGNORECASE);
    # SYMATTR Description value       
    
    reIsSAttrGeneric = re.compile(r'^[\s]*SYMATTR[\s]+([\S]+)[\s]+(.*)', flags=re.IGNORECASE);
    # SYMATTR kind value       
    
    
    attrid2attr = {0:'InstName',3:'Value',123:'Value2',39:'SpiceLine',40:'SpiceLine2',38:'SpiceModel'};
    attr2attrid = {'InstName':0,'Value':3, 'Value2':123, 'SpiceLine':39, 'SpiceLine2':40,'SpiceModel':38};
    
    lastComponent = None;
    lastWire = None;
    lastLabel = None;
    lastText = None;
    lastPin =None;
    lastSymbol =None;
    lastAttributesDict = {};
    
    lastLine = '';
    lastSymLine = '';
    linecnt = 0;
    symlinecnt = 0;
    translinecnt = 0;
    config = None;
    
    def __init__(self):
        self.circDict = CircuitDict();
        self.symbolDict = SymbolDict();
        self.validInputFile = False;
        #self.lt2tscale = 1.0/32.0;
        #self.lt2tscale = (1.0/64.0);
        self.lt2tscale = (1.0/48.0);
        self.includepreamble = True;
        self.lastASCfile = None;
        
        try:
            approot2 = (os.path.dirname(os.path.realpath(__file__)));
            approot = os.path.dirname(os.path.abspath(__file__))
        except NameError:  # We are the main py2exe script, not a module
            import sys
            approot = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        self.scriptdir = (approot);
        
        self.symfilebasepath = 'sym'+os.sep;
        
        configfileloc = self.scriptdir+os.sep+'lt2ti.ini'
        print('lt2ti: Loading config at "'+configfileloc+'"')
        
        self.config = configparser.RawConfigParser()
        self.config.read(configfileloc)
        
        if (self.config.has_option('general', 'symdir')):
            self.symfilebasepath = self.config.get('general', 'symdir') + os.sep;
            
        self.config = configparser.RawConfigParser()
        conffiles = self.config.read([self.scriptdir+os.sep+'lt2ti.ini', self.scriptdir+os.sep+ self.symfilebasepath + 'sym.ini'])
        
        if (self.config.has_option('general', 'lt2tscale')):
            self.lt2tscale = float(self.config.get('general', 'lt2tscale'));
        if (self.config.has_option('general', 'lt2tscale_inverse')):
            self.lt2tscale = 1.0/float(self.config.get('general', 'lt2tscale_inverse'));        
        if (self.config.has_option('general', 'includepreamble')):
            includepreamble = self.config.get('general', 'includepreamble');
            self.includepreamble = ((str(includepreamble).lower() == 'true') or ((includepreamble) == '1'))
            
        print('lt2ti ready for conversion.')

    

            
    def _symresetSymbol(self):
        
        if (self.lastPin != None):
            if (self.lastSymbol != None):
                self.lastSymbol.addPin(self.lastPin);
                
            self.lastPin = None;        
        
        if (self.lastSymbol != None):
            self.symbolDict.addSymbol(self.lastSymbol);
            self.lastSymbol = None;

    def symresetPin(self):
        if (self.lastPin != None):
            if (self.lastSymbol != None):
                self.lastSymbol.addPin(self.lastPin);
                
            self.lastPin = None;                
        return;
            
    def readASYFile(self, relfileandpath):
        print('Loading Symbol file "'+relfileandpath+'"...')
        # read symbol file
        self.symlinecnt = 0;
        aSymbol = None;
        
        try :
            fhy = open(self.scriptdir+os.sep+ relfileandpath, mode='r', newline=None);
        except Exception as e:
            print('could not open ASY file "'+relfileandpath+'"  (cwd="'+os.curdir+'")');
            return None;        
        
        for line in fhy:
            self.symlinecnt = self.symlinecnt + 1;
            self.lastSymLine = line;
            
            m = self.reIsHdr.match(line);
            if (m != None):
                print('valid file header found:'+line);
                self.validInputFile = True;
                continue;
            
            m = self.reIsSym.match(line);
            if (m != None):
                print('symbol of type '+m.group(1)+': '+line);
                self._handleSType(m);
                continue;
            
            m = self.reIsSAttrPrefix.match(line);
            if (m != None):
                self._handleSymPrefix(m);
                continue;            
            
            m = self.reIsSAttrDescr.match(line);
            if (m != None):
                self._handleSymDescr(m);
                continue;                        
            
            m = self.reIsSAttrValue.match(line);
            if (m != None):
                self._handleSymValue(m);
                continue;
            
            m = self.reIsSAttrGeneric.match(line);
            if (m != None):
                self._handleSymAttrGeneric(m);
                continue;            
            
            m = self.reIsPin.match(line);
            if (m != None):
                self._handleSymPin(m);
                continue;
            
            m = self.reIsPinName.match(line);
            if (m != None):
                self._handleSymPinName(m);
                continue;
                
            m = self.reIsPinOrder.match(line);
            if (m != None):
                self._handlePinOrder(m);
                continue;
                

            
            print("could not match symbol line '"+line.replace('\n','')+"'");
        aSymbol = self.lastSymbol;
        self._symresetSymbol(); # handle last item
        
        fhy.close(); 
        return aSymbol;
    
    def readASY2TexFile(self, relfileandpath, symbol):
        asy2texfileandpath = self.scriptdir+os.sep+ relfileandpath
        try :
            fht = open(asy2texfileandpath, mode='r', newline=None);
        except Exception as e:
            print('Could not open requested asy2tex tile: "'+relfileandpath+'" (cwd="'+os.curdir+'")');
            return None;        
        
        print('Processing asy2tex file: "'+relfileandpath+'" (cwd="'+os.curdir+'")');
        
        rAliasFile = re.compile(r'ALIASFOR (.*\.asy2tex)[\s]*$', flags=re.IGNORECASE);
        
        
        rType = re.compile(r'^[\s]*Type[\s]+([\S]+)', flags=re.IGNORECASE); # compile(r'^[\s]*SYMATTR[\s]+([\S]+)[\s]+(.*)', flags=re.IGNORECASE);
        rOriginTex = re.compile(r'^[\s]*TexOrigin[\s]+([-\d\.]+)[\s]+([-\d\.]+)[\s]+([-\d]+)[\s]+([01TRUEtrueFALSEfalse]+)', flags=re.IGNORECASE); 
        rOriginSym = re.compile(r'^[\s]*SymOrigin[\s]+([-\d\.]+)[\s]+([-\d\.]+)[\s]+([-\d]+)[\s]+([01TRUEtrueFALSEfalse]+)', flags=re.IGNORECASE); 
        #                                          x1             y1           rot       mirror
        
        rPinList_be = re.compile(r'^[\s]*(BeginPinList)[\s]*$', flags=re.IGNORECASE); 
        
        rPinListEntry = re.compile(r'^[\s]*([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]+([-\d]+)[\s]+(.*)$', flags=re.IGNORECASE); 
        #                                    ord          x1            y1          rot        length       PinName
        
        rPinList_en = re.compile(r'^[\s]*(EndPinList)[\s]*$', flags=re.IGNORECASE); 
        
        rConKV_be = re.compile(r'^[\s]*(BeginConversionKeyvals)[\s]*$', flags=re.IGNORECASE); #BeginConversionKeyvals
        rConKV_en = re.compile(r'^[\s]*(EndConversionKeyvals)[\s]*$', flags=re.IGNORECASE); #EndConversionKeyvals
        rConvKVList = re.compile(r'([^=]+)=(.*)$', flags=re.IGNORECASE); 
        
        
        rTexName = re.compile(r'^[\s]*TexElementName[\s]+(.*)$', flags=re.IGNORECASE); 
        rTex_be = re.compile(r'^[\s]*(BeginTex)[\s]*$', flags=re.IGNORECASE); 
        rTex_en = re.compile(r'^[\s]*(EndTex)[\s]*$', flags=re.IGNORECASE);         
        
        ispinlist = False;
        istexlist = False;
        isconvkv = False;
        
        texlist = [];
        
        aTSymbol = copy.deepcopy(symbol);
        
        self.translinecnt = 0;
        for line in fht:
            self.translinecnt = self.translinecnt+1;
            
            m = rAliasFile.match(line);
            if ((m != None) and (self.translinecnt < 2)): # must be at the beginning
                fht.close();
                pathtofile = os.path.dirname(asy2texfileandpath);
                aliasfile = m.group(1);
                aliasfileandpath = pathtofile+os.sep+aliasfile;
                relaliasfileandpath = os.path.relpath(aliasfileandpath,  self.scriptdir+os.sep);
                print('Found an alias entry: "'+aliasfile+'" which resolved to "'+aliasfileandpath+'" and "'+relaliasfileandpath+'" ');
                aTSymbol = self.readASY2TexFile(relaliasfileandpath, symbol);
                return aTSymbol;
            
            m = rPinList_be.match(line);
            if (m != None):            
                ispinlist = True;
                continue;
            
            m = rPinList_en.match(line);
            if (m != None):            
                ispinlist = False;
                continue;            
            
            if (ispinlist):
                m = rPinListEntry.match(line);
                if (m != None):
                    # add pinlist entry
                    # Pinlist entry:          ord         x1             y1        rot        length       PinName
                    lxPin = SymPin();
                    lxPin.order = m.group(1);
                    lxPin.x1 = m.group(2);
                    lxPin.y1 = m.group(3);
                    lxPin.rot = m.group(4);
                    lxPin.length = m.group(5);
                    lxPin.name = m.group(6);
                    
                    aTSymbol.latexPins.addPin(lxPin);
                continue;
            
            m = rConKV_be.match(line);
            if (m != None):
                ispinlist = False;
                istexlist = False;
                isconvkv = True;
                continue;
            
            m = rConKV_en.match(line);
            if (m != None):
                ispinlist = False;
                istexlist = False;
                isconvkv = False;
                continue;            
            
            if (isconvkv):
                m = rConvKVList.match(line);
                if (m != None):
                    aTSymbol.conversionKV[m.group(1)] = m.group(2);
                continue;
            
            m = rTex_be.match(line);
            if (m != None):            
                ispinlist = False;
                istexlist = True;
                isconvkv = False;
                continue;               
                
            m = rTex_en.match(line);
            if (m != None):
                ispinlist = False;
                istexlist = False;
                isconvkv = False;
                continue;
                
            if (istexlist):
                texlist.append(line);
                continue;
            
            m = rTexName.match(line);
            if (m != None):
                aTSymbol.latexElementName = m.group(1);
                continue;            
            
            m = rType.match(line);
            if (m != None):
                aTSymbol.latexType = m.group(1);
                continue;
                
            m = rOriginTex.match(line);
            if (m != None):
                aTSymbol.latexOriginX1 = float(m.group(1));
                aTSymbol.latexOriginY1 = float(m.group(2));
                aTSymbol.latexOriginRot = int(m.group(3));
                aTSymbol.latexOriginMirror = ((m.group(4) == '1') or (str.lower(m.group(4)) == 'true'));
                continue;
            
            m = rOriginSym.match(line);
            if (m != None):
                aTSymbol.symbolOriginX1 = float(m.group(1));
                aTSymbol.symbolOriginY1 = float(m.group(2));
                aTSymbol.symbolOriginRot = int(m.group(3));
                aTSymbol.symbolOriginMirror = ((m.group(4) == '1') or (str.lower(m.group(4)) == 'true'));
                continue;            
                
            print("coult not match line "+str(self.translinecnt)+" in asy2tex file '"+relfileandpath+"' :"+line);
        
        aTSymbol.latexTemplate = texlist;
            
        fht.close();
        return aTSymbol;
    
        
    def _handleSType(self, m):
        self._symresetSymbol(); # no more attributes for previous lines
        
        self.lastSymbol = Symbol(m.group(1))
        self.lastSymbol.lt2tscale = self.lt2tscale;
        return; 
    
    def _handleSymPrefix(self, m):
        self.lastSymbol.prefix = m.group(1);
        self.lastSymbol.attributes['Prefix'] = m.group(1);
        return;
    
    def _handleSymDescr(self, m):
        self.lastSymbol.description = m.group(1);
        self.lastSymbol.attributes['Description'] = m.group(1);
        return;    
    
    def _handleSymValue(self, m):
        self.lastSymbol.value = m.group(1);
        self.lastSymbol.attributes['Value'] = m.group(1);
        return;
    
    def _handleSymAttrGeneric(self, m):
        self.lastSymbol.attributes[m.group(1)] = m.group(2);
        return;


    def _handleSymPin(self, m):
        self.symresetPin();
        self.lastPin = SymPin();
        self.lastPin.x1 = int(m.group(1));
        self.lastPin.y1 = int(m.group(2));
        self.lastPin.labelpos = (m.group(3));
        self.lastPin.labeloffset = int(m.group(4));
        return;
    
    def _handleSymPinName(self, m):
        self.lastPin.name = m.group(1);
        
    def _handlePinOrder(self, m):
        self.lastPin.order = int(m.group(1));

    def _resetLast(self):
        if (len(self.lastAttributesDict) > 0):
            for aid, attr in self.lastAttributesDict.items():
                self.lastComponent.addAttribute(attr);
            self.lastAttributesDict = {};
            
        if (self.lastComponent != None):
            self.circDict.addComponent(self.lastComponent);
            self.lastComponent = None;
            
        if (self.lastWire != None):
            self.circDict.addWire(self.lastWire);
            self.lastWire = None;
            
        if (self.lastLabel != None):
            self.circDict.addNetLabel(self.lastLabel);
            self.lastLabel = None;
        
        if (self.lastText != None):
            self.circDict.addText(self.lastText);
            self.lastText = None;       
    
    def readASCFile(self, fileandpath):
        print('Reading ASC file "'+fileandpath+'"...')
        self.lastComponent = None;
        self.lastSymbol = None;
        self.lastAttributesDict = {};
        self.lastLabel = None;
        self.lastWire = None
        self.lastPin = None;
        self.circDict = CircuitDict();
        self.symbolDict = SymbolDict();
        self.lastText = None
        self.lastASCfile = fileandpath;
        
        self.linecnt = 0;
        try :
            fhs = open(fileandpath, mode='r', newline=None);
        except Exception as e:
            print('could not open ASC file "'+fileandpath+'" (cwd="'+os.curdir+'")');
            return None;
        
        
        for line in fhs:
            self.linecnt = self.linecnt + 1;
            self.lastLine = line;
            
            m = self.reIsHdr.match(line);
            if (m != None):
                print('valid file header found:'+line);
                self.validInputFile = True;
                continue;
            m = self.reIsSheet.match(line);
            if (m != None):
                print('sheet: '+line);
                continue;
                
            m = self.reIsNetLabel.match(line);
            if (m != None):
                self._handleNetLabel(m);
                continue;
            
            m = self.reIsComponent.match(line);
            if (m != None):
                self._handleComponent(m);
                continue;
                
            m = self.reIsCAttrName.match(line);
            if (m != None):
                self._handleComponentName(m);
                continue;
                
            m = self.reIsCAttrValue.match(line);
            if (m != None):
                self._handleComponentValue(m);
                continue;
            
            m = self.reIsCAttrValue2.match(line);
            if (m != None):
                self._handleComponentValue2(m);
                continue;
                
            m = self.reIsCAttrGeneric.match(line);
            if (m != None):
                self._handleAttributeGeneric(m);            
                continue;
                
            m = self.reIsWire.match(line);
            if (m != None):
                self._handleWire(m);
                continue;
                
            m = self.reIsWindow.match(line);
            if (m != None):
                self._handleWindow(m);
                continue;
            
            m = self.reIsText.match(line);
            if (m != None):
                self._handleText(m);            
                continue;
            
            m = self.reIsLine.match(line);
            if (m != None):
                self._handleLine(m);            
                continue;            
            
            m = self.reIsRect.match(line);
            if (m != None):
                self._handleRect(m);            
                continue;                        
            
            m = self.reIsCircle.match(line);
            if (m != None):
                self._handleCircle(m);            
                continue;             
            
            print("could not match line '"+line.replace('\n','')+"'");
        self._resetLast(); # handle last item
        
        fhs.close();
        return self.circDict;
    
    def _handleNetLabel(self, m):
        self._resetLast(); # no more attributes for previous lines
        # FLAG <x1> <y1> <label>
        if (m.group(3) == '0'): # more a ground symbol than a net label
            c = Component(r'circuiTikz\\gnd', int(m.group(1)), int(m.group(2)), 0, False, 'GND'+str(self.linecnt), '')
            self._handleComponent_worker(c);
        else:
            lbl = NetLabel(m.group(3), int(m.group(1)), int(m.group(2)));
            lbl.value = 'lbl'+str(self.linecnt)
            
            pathandctype = 'netlabel';
            if not self.symbolDict.hasSymbolPath(pathandctype):
                # not cached, try to load
                fullpath = self.symfilebasepath + pathandctype.replace('\\\\','\\');
                sym = self.readASYFile(fullpath+'.asy');
                sym.path = '';
                sym.ctype = pathandctype;
                sym.pathandctype = pathandctype;
                
                tsym = self.readASY2TexFile(fullpath+'.asy2tex',sym);
                if (tsym != None):
                    self.symbolDict.addSymbol(tsym); # add symbol and translation information
            else:
                # already existing in cache
                tsym = self.symbolDict.getSymbolByPath(pathandctype);
                
            lbl.symbol = tsym;            
            
            self.lastLabel = lbl;
        return;
    
    def _handleComponent(self, m):
        self._resetLast(); # no more attributes for previous lines
        # SYMBOL path\\type x1 x2 [R|M] rotation

        # Component ( ctype,       x1,              y1,                rot,          mirror,                            name, value)
        c = Component(m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(5)), (str.upper(m.group(4)) == 'M'),  '', "");
        self._handleComponent_worker(c);
    
    def _handleComponent_worker(self, c):
        
        if not self.symbolDict.hasSymbolPath(c.pathandctype):
            # not cached, try to load
            fullpath = self.symfilebasepath + c.pathandctype.replace('\\\\','\\');
            sym = self.readASYFile(fullpath+'.asy');
            sym.path = c.path;
            sym.ctype = c.ctype;
            sym.pathandctype = c.pathandctype;
            
            tsym = self.readASY2TexFile(fullpath+'.asy2tex',sym);
            if (tsym != None):
                self.symbolDict.addSymbol(tsym); # add symbol and translation information
        else:
            # already existing in cache
            tsym = self.symbolDict.getSymbolByPath(c.pathandctype);
            
        c.symbol = tsym;
        
        
        
        self.lastComponent = c;
        
        print('Found component: \n'+c.asString('    '));
        
        return;    
    
    def _handleComponentName(self, m):
        # SYMATTR InstName <name>
        self.lastComponent.name = m.group(1);
        attrkind = 'InstName';
        attrval = m.group(1);
        if (not attrkind in self.lastAttributesDict):
            attr = Attribute(attrkind, attrval);
        else:
            attr = self.lastAttributesDict[attrkind];
            attr.value = attrval;

        if (attrval != "*"):
            attr.visible = True;
        self.lastAttributesDict[attr.kind] = attr;
        return; 
    
    def _handleComponentValue(self, m):
        # SYMATTR Value <value>
        attrkind = 'Value';
        attrval = m.group(1);
        if (attrval == '""'): # this is the way LTspice indicates an empty value
            attrval = '';

        self.lastComponent.value = attrval;
        
        if (not attrkind in self.lastAttributesDict):
            attr = Attribute(attrkind, attrval);
        else:
            attr = self.lastAttributesDict[attrkind];
            attr.value = attrval;
        
        if (attrval != "*"):
            attr.visible = True;
        self.lastAttributesDict[attr.kind] = attr;
        return; 
    
    def _handleComponentValue2(self, m):
        #SYMATTR Value2 <value>
        self.lastComponent.value2 = m.group(1);
        attrkind = 'Value2';
        attrval = m.group(1);
        if (not attrkind in self.lastAttributesDict):
            attr = Attribute(attrkind, attrval);
        else:
            attr = self.lastAttributesDict[attrkind];
            attr.value = attrval;

        if (attrval != "*"):
            attr.visible = True;
        self.lastAttributesDict[attr.kind] = attr;
        return; 
    
    def _handleAttributeGeneric(self, m):
        #SYMATTR <attrib.name> <value>
        attrkind = m.group(1);
        attrval = m.group(2);
        if (not attrkind in self.lastAttributesDict):
            attr = Attribute(attrkind, attrval);
            self.lastAttributesDict[attr.kind] = attr;
        else:
            attr = self.lastAttributesDict[attrkind];
            attr.value = attrval;
            self.lastAttributesDict[attr.kind] = attr;
        return;    
    
    
    def _handleWire(self, m):
        self._resetLast(); # no more attributes for previous lines
            # WIRE <x1> <y1> <x2> <y2>
        self.lastWire = Wire("w"+str(self.linecnt),int(m.group(1)),int(m.group(2)), int(m.group(3)), int(m.group(4)))
        return;
    
    def _handleWindow(self, m): # attribute display position
        # WINDOW  attr.No.Id   rel.x1     rel y1       pos.str.    size?=2
        attrid = int(m.group(1));
        if (attrid in self.attrid2attr):
            attrkind = self.attrid2attr[attrid];
        else:
            print("Could not match attr.id="+m.group(1)+" to an attribute.")
            return;
        
        if (attrkind in self.lastAttributesDict):
            # attribute exists: modify its values
            attr = self.lastAttributesDict[attrkind];
        else: # create new
            attr = Attribute(attrkind, 'undefined');
        
        attr.visible = True;
        attr.idnum = m.group(1);
        attr.x1rel = int(m.group(2));
        attr.y1rel = int(m.group(3));
        attr.align = m.group(4);
        attr.size  = float(m.group(5));
        
        self.lastAttributesDict[attrkind] = attr;
        return;
    
    def _handleText(self, m): # attribute display position
        self._resetLast(); # no more attributes for previous lines
        # TEXT x1          y1       pos.str.    size?=2         string
        txt = SchText(m.group(5), int(m.group(1)), int(m.group(2)))
        txt.align = m.group(3);
        txt.size = float(m.group(4));
        
        txt.value = 'lbl'+str(self.linecnt)
        
        pathandctype = 'text';
        if not self.symbolDict.hasSymbolPath(pathandctype):
            # not cached, try to load
            fullpath = self.symfilebasepath + pathandctype.replace('\\\\','\\');
            sym = self.readASYFile(fullpath+'.asy');
            sym.path = '';
            sym.ctype = pathandctype;
            sym.pathandctype = pathandctype;
            
            tsym = self.readASY2TexFile(fullpath+'.asy2tex',sym);
            if (tsym != None):
                self.symbolDict.addSymbol(tsym); # add symbol and translation information
        else:
            # already existing in cache
            tsym = self.symbolDict.getSymbolByPath(pathandctype);
            
        txt.symbol = tsym;            
        
        self.lastText = txt;        
        
        return;
    
    def _handleLine(self, m):
        if ((m.group(6)) != ''):
            lstyle = int(m.group(6));
        else:
            lstyle = 0;
        
        schline = SchLine(int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), lstyle)
        schline.kind = (m.group(1));
        
        pathandctype = 'SchLine';
        if not self.symbolDict.hasSymbolPath(pathandctype):
            # not cached, try to load
            fullpath = self.symfilebasepath + pathandctype.replace('\\\\','\\');
            #sym = self.readASYFile(fullpath+'.asy');
            sym = Symbol(pathandctype);
            sym.lt2tscale = self.lt2tscale;
            sym.path = '';
            sym.ctype = pathandctype;
            sym.pathandctype = pathandctype;
            
            tsym = self.readASY2TexFile(fullpath+'.asy2tex',sym);
            if (tsym != None):
                self.symbolDict.addSymbol(tsym); # add symbol and translation information
        else:
            # already existing in cache
            tsym = self.symbolDict.getSymbolByPath(pathandctype);
            
        schline.symbol = tsym;            
        self.circDict.addSchLine(schline);
        return;        
    
    def _handleRect(self, m):
        if ((m.group(6)) != ''):
            lstyle = int(m.group(6));
        else:
            lstyle = 0;        
        schrect = SchRect(int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), lstyle)
        schrect.kind = (m.group(1));
        
        pathandctype = 'SchRect';
        if not self.symbolDict.hasSymbolPath(pathandctype):
            # not cached, try to load
            fullpath = self.symfilebasepath + pathandctype.replace('\\\\','\\');
            #sym = self.readASYFile(fullpath+'.asy');
            sym = Symbol(pathandctype);
            sym.lt2tscale = self.lt2tscale;
            sym.path = '';
            sym.ctype = pathandctype;
            sym.pathandctype = pathandctype;
            
            tsym = self.readASY2TexFile(fullpath+'.asy2tex',sym);
            if (tsym != None):
                self.symbolDict.addSymbol(tsym); # add symbol and translation information
        else:
            # already existing in cache
            tsym = self.symbolDict.getSymbolByPath(pathandctype);
            
        schrect.symbol = tsym;            
        self.circDict.addSchLine(schrect);
        return;        
    
    def _handleCircle(self, m):
        if ((m.group(6)) != ''):
            lstyle = int(m.group(6));
        else:
            lstyle = 0;        
        schcirc = SchCirc(int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), lstyle)
        schcirc.kind = (m.group(1));
        
        pathandctype = 'SchCirc';
        if not self.symbolDict.hasSymbolPath(pathandctype):
            # not cached, try to load
            fullpath = self.symfilebasepath + pathandctype.replace('\\\\','\\');
            #sym = self.readASYFile(fullpath+'.asy');
            sym = Symbol(pathandctype);
            sym.lt2tscale = self.lt2tscale;
            sym.path = '';
            sym.ctype = pathandctype;
            sym.pathandctype = pathandctype;
            
            tsym = self.readASY2TexFile(fullpath+'.asy2tex',sym);
            if (tsym != None):
                self.symbolDict.addSymbol(tsym); # add symbol and translation information
        else:
            # already existing in cache
            tsym = self.symbolDict.getSymbolByPath(pathandctype);
            
        schcirc.symbol = tsym;            
        self.circDict.addSchLine(schcirc);
        return;            
    
    def copyFileContents(self,source,destination):
        fhs = open(source, mode='r', newline='');
        fhd = open(destination, mode='a', newline=''); # prevent automatic newline conversion to have more control over nl chars.
        for line in fhs:
            #print('copying line "'+line+'" from source to destination');
            fhd.write(line);
        fhd.close();
        fhs.close();    
        
    def copyFile(self,source,destination):
        fhs = open(source, mode='r', newline='');
        fhd = open(destination, mode='w', newline=''); # prevent automatic newline conversion to have more control over nl chars.
        for line in fhs:
            #print('copying line "'+line+'" from source to destination');
            fhd.write(line);
        fhd.close();
        fhs.close();    
        
    def copyFileContentsToHandle(self,source,hdestination):
        fhs = open(source, mode='r', newline=None);
        for line in fhs:
            #print('copying line "'+line+'" from source to destination');
            hdestination.write(line);
        fhs.close();               
    
    def writeCircuiTikz(self, outfile):
        print('Writing Tex commands to "'+outfile+'"...')
        xscale = 1 * self.lt2tscale;
        yscale = -1 * self.lt2tscale; # y is inverse for LTspice files
        xoffset = 0;
        yoffset = 0;
        
        fhd = open(outfile, mode='w', newline='\r\n'); # prevent automatic newline conversion to have more control over nl chars.
        
        if (self.includepreamble):
            self.copyFileContentsToHandle(self.scriptdir+os.sep+ self.symfilebasepath+'latex_preamble.tex', fhd);
            
            if (self.config.has_option('general','latexincludes')):
                incfiles = self.config.get('general','latexincludes');
                
                incfiles = incfiles.split(';');
                for incfile in incfiles:
                    srcfile = self.scriptdir+os.sep+ self.symfilebasepath + incfile;
                    dstfile = os.path.dirname(outfile) +os.sep + os.path.basename(incfile);
                    self.copyFile(srcfile, dstfile)
            
            
        if (self.config.has_option('general','bipoles_length')):
            bipoles_length = self.config.get('general','bipoles_length');
            fhd.write(r'\ctikzset{bipoles/length='+bipoles_length+'}\n');
        

        
        self.circDict.wiresToPolyWires();
        
        #output wires:
        wireDict = self.circDict.getWiresByCoord();
        for pp, dictWires in wireDict.items():
            # all wires at the pp position
            
            #jcnt = self.circDict.getJunctionCound(pp);
            jcnt = self.circDict.getJunctionCount(pp);
            
            if (jcnt <= 2): # no junction
                p1junction = '';
            else: # junction
                p1junction = '*';
                
            for uuid, wire in dictWires.items():
                pp1 = wire.getP1Tuple();
                if (pp1 == pp): # only draw wire if pos1 is attached. Otherwise wires will get drawn multiple times.
                    pp2 = wire.getP2Tuple();
                    
                    jcnt2 = self.circDict.getJunctionCount(pp2);
                    if (jcnt2 <= 2):
                        p2junction = '';
                    else:
                        p2junction = '*';
                    
                    x1 = pp[0]*xscale+xoffset;
                    y1 = pp[1]*yscale+yoffset;
                    x2 = pp2[0]*xscale+xoffset;
                    y2 = pp2[1]*yscale+yoffset;
                        
                    lenxn = 0;
                    if ((type(wire) is PolyWire)):
                        lenxn = len(wire.xn);
                    if ( ((type(wire) is Wire) and not (type(wire) is PolyWire)) or ( (type(wire) is PolyWire) and ( len(wire.xn) <= 0) )): # normal wire or polywire with no intermediate segments
                        # \draw (8,2)to[*short,*-] (8,4);%
                        fhd.write(r'\draw [/lt2ti/Net]('+str(x1)+r','+str(y1)+r')to[*short,'+p1junction+'-'+p2junction+', color=netcolor] ('+str(x2)+','+str(y2)+');% wire '+wire.name+'\n');
                    else:
                        # polywire
                        # \draw (4,2) -- (4,4) -- (6,4);
                        xn = wire.xn;
                        yn = wire.yn;
                        x1b = xn[0]*xscale+xoffset;
                        y1b = yn[0]*yscale+yoffset;
                        
                        x2b = xn[len(xn)-1]*xscale+xoffset;
                        y2b = yn[len(yn)-1]*yscale+yoffset;
                        # normal wire segments for junctions: (this works with zero length segements, so we do not use the x1b/y1b, x2b/y2b points any longer.)
                        fhd.write(r'\draw [/lt2ti/Net]('+str(x1)+r','+str(y1)+r')to[*short,'+p1junction+'-, color=netcolor] ('+str(x1)+','+str(y1)+');% wire '+wire.name+' start\n');
                        fhd.write(r'\draw [/lt2ti/Net]('+str(x2)+r','+str(y2)+r')to[*short,-'+p2junction+', color=netcolor] ('+str(x2)+','+str(y2)+');% wire '+wire.name+' end\n');                        
                          #fhd.write(r'\draw [/lt2ti/Net]('+str(x1)+r','+str(y1)+r')to[*short,'+p1junction+'-] ('+str(x1b)+','+str(y1b)+');% wire '+wire.name+' start\n');
                          #fhd.write(r'\draw [/lt2ti/Net]('+str(x2b)+r','+str(y2b)+r')to[*short,-'+p2junction+'] ('+str(x2)+','+str(y2)+');% wire '+wire.name+' end\n');
                        # polyline
                        wstr = '\draw [/lt2ti/Net]('+str(x1)+r','+str(y1)+r')';
                        for i in range(0, (len(xn))):
                            xni = xn[i]*xscale+xoffset;
                            yni = yn[i]*yscale+yoffset;
                            wstr = wstr + ' -- '
                            wstr = wstr + ' ('+str(xni)+','+str(yni)+')' ;
                        wstr = wstr + ' -- ('+str(x2)+','+str(y2)+'); % wire '+wire.name+ ' polyline \n' ;
                        fhd.write(wstr);
        # output components
        for pp, compDict in self.circDict.coordCompDict.items():
            for c, comp in compDict.items():
                comp.circuitDict = self.circDict; # used for junction lookup etc.
                comp.config = self.config; # allow config parameters in components to be used
                
                texlines = comp.translateToLatex({}); # ToDo: apply xoffset, yoffset (currently not in use)
                
                for tl in texlines:
                    tl = re.sub(r'[\r]*[\n]$', '', tl); # remove trailing line break since we add it after the comment.
                    fhd.write(tl+' % component "'+comp.pathandctype+'" "'+comp.name+'" \n');
        
        
        # output labels
        for pp, labeldict in self.circDict.coordLabelDict.items():
            for l, label in labeldict.items():
                label.circuitDict = self.circDict;
                
                texlines = label.translateToLatex({}); # ToDo: apply xoffset, yoffset (currently not in use)
                
                for tl in texlines:
                    tl = re.sub(r'[\r]*[\n]$', '', tl); # remove trailing line break since we add it after the comment.
                    fhd.write(tl+' % label "'+label.pathandctype+'" "'+label.label+'" '+label.value+' \n');
                
        # output text
        for pp, txtdict in self.circDict.coordTextDict.items():
            for l, txt in txtdict.items():
                txt.circuitDict = self.circDict;
                
                texlines = txt.translateToLatex({}); # ToDo: apply xoffset, yoffset (currently not in use)
                
                for tl in texlines:
                    tl = re.sub(r'[\r]*[\n]$', '', tl); # remove trailing line break since we add it after the comment.
                    fhd.write(tl+' % text "'+txt.pathandctype+'" "'+txt.text+' '+txt.value+' " \n');                
                    
                    
        # output lines
        for uuid, schline in self.circDict.getSchLines():
            schline.circuitDict = self.circDict;
            texlines = schline.translateToLatex({}); # ToDo: apply xoffset, yoffset (currently not in use)
            for tl in texlines:
                tl = re.sub(r'[\r]*[\n]$', '', tl); # remove trailing line break since we add it after the comment.
                fhd.write(tl+' % schLine "'+schline.pathandctype+'" '+str(schline.getP1Tuple())+'->'+str(schline.getP2Tuple())+' style='+str(schline.style)+'\n');
        # output rects
        for uuid, schrect in self.circDict.getSchRects():
            schrect.circuitDict = self.circDict;
            texlines = schrect.translateToLatex({}); # ToDo: apply xoffset, yoffset (currently not in use)
            for tl in texlines:
                tl = re.sub(r'[\r]*[\n]$', '', tl); # remove trailing line break since we add it after the comment.
                fhd.write(tl+' % schRect "'+schrect.pathandctype+'" '+str(schrect.getP1Tuple())+'->'+str(schrect.getP2Tuple())+' style='+str(schrect.style)+'\n');

        if (self.includepreamble):
            self.copyFileContentsToHandle(self.scriptdir+os.sep+ self.symfilebasepath+'latex_closing.tex', fhd);

        fhd.close();
        print("Done.");
        return;




class CircuitDict:
    
    def __init__(self):
        self.coordWireDict = {} # todo: refactor into SpatialDicts
        self.wireDict = {}
        self.coordCompDict = {}
        self.compDict = {}
        self.labelDict = {}
        self.coordLabelDict = {}
        self.textDict = {}
        self.coordTextDict = {}
        self.coordCompPinDict = {}
        
        self.lineDict = SpatialDict()
        self.lineDict.objidattrib = 'uuid'
        self.lineDict.objposattrib = ['getP1Tuple', 'getP2Tuple'];
        
        self.rectDict = SpatialDict()
        self.rectDict.objidattrib = 'uuid'
        self.rectDict.objposattrib = ['getP1Tuple', 'getP2Tuple'];
        
    def addSchLine(self, aLine):
        self.lineDict.addObj(aLine)
    def removeSchLine(self, aLine):
        self.lineDict.removeObj(aLine)
    def getSchLines(self):
        return self.lineDict.getAllObjs()
    
    def addSchRect(self, aRect):
        self.rectDict.addObj(aRect)
    def removeSchRect(self, aRect):
        self.rectDict.removeObj(aRect)
    def getSchRects(self):
        return self.rectDict.getAllObjs()
        
    def addNetLabel(self, aLabel):
        self.labelDict[aLabel.uuid] = aLabel;
        pp = (aLabel.x1, aLabel.y1);
        if (pp in self.coordLabelDict):
            dictLbls = self.coordLabelDict[pp];
        else:
            dictLbls = {};
        dictLbls[aLabel.uuid] = aLabel;
        self.coordLabelDict[pp] = dictLbls;
    
    def removeNetLabel(self, aLabel):
        self.labelDict.pop(aLabel.uuid,None);
        pp = (aLabel.x1, aLabel.y1);
        dictLbls = self.coordLabelDict[pp];
        dictLbls.pop(aLabel.uuid,None);
        self.coordLabelDict[pp] = dictLbls;    
        
    def addText(self, aText):
        self.textDict[aText.uuid] = aText;
        pp = (aText.x1, aText.y1);
        if (pp in self.coordTextDict):
            dictTxts = self.coordLabelDict[pp];
        else:
            dictTxts = {};
        dictTxts[aText.uuid] = aText;
        self.coordTextDict[pp] = dictTxts;
        
    def removeText(self, aText):
        self.textDict.pop(aText.uuid,None);
        pp = (aText.x1, aText.y1);
        dictTxts = self.coordTextDict[pp];
        dictTxts.pop(aText.uuid,None);
        self.coordTextDict[pp] = dictTxts;
        
    def addComponent(self, aComp):
        self.compDict[aComp.uuid] = aComp;
        pp = (aComp.x1, aComp.y1);
        if (pp in self.coordCompDict):
            cdict = self.coordCompDict[pp];
        else:
            cdict = {};
        cdict[aComp.uuid] = aComp;
        self.coordCompDict[pp] = cdict;
        
        if aComp.symbol != None:
            pindictlist = aComp.symbol.symbolPins.getAllPins();
            for pname, pin in pindictlist:
                self.addComponentPin(aComp, pin);
            
    def addComponentPin(self, aComp, aPin):
        pp = aComp.getAbsolutePinPos(aPin);
        ppint = (int(round(pp[0])), int(round(pp[1]))); # use integer, since the AbsolutePinPos might have produced roundoff errors during rotation/shifting.
        #pp = (pin.x1 + aComp.x1, pin.y1 + aComp.y1) # convert to absolute position
        if (ppint in self.coordCompPinDict):
            dictComps = self.coordCompPinDict[ppint];
        else:
            dictComps = {};
        dictComps[aComp.uuid] = aComp;
        self.coordCompPinDict[ppint] = dictComps;        

    def _removeComponent_compDic(self, cmpDict, aComp):
        res = compDict.Pop(aComp.uuid, None);
        if res != None:
            return True;
        return False;
        
    def _removeComponent_coordDic(self, coordCDict, aComp):
        cnt = 0;
        pinPosList = aComp.getPinPosList();
        for pp in pinPosList:
            if (pp in coordCDict):
                dictComps = coordCDict[pp];
                res = dictComps.Pop(aComp.uuid,None);
                if (res != None):
                    cnt = cnt+1;
                coordCDict[pp] = dictComps;
            
        if (cnt == len(pinPosList)):
            return True;
        return False;
    
    def removeComponent(self, aComp):
        success = True;
        success = success and _removeComponent_compDic(self, self.compDict, aComp);
        success = success and _removeComponent_coordDic(self, self.coordCompDict, aComp);
        # todo: remove pins
    
    def _removeWire_wireDic(self, dic, aWire):
        res = dic.pop(aWire.uuid,None)
        if res == None:
            return False;
        else:
            return True;
        
    def _removeWire_coordDic(self, dic, aWire):
        success = True;
        p1 = aWire.getP1Tuple();
        wd = dic[p1];
        success = success and self._removeWire_wireDic(wd, aWire);
        dic[p1] = wd;
        
        p2 = aWire.getP2Tuple();
        wd = dic[p2];
        success = success and self._removeWire_wireDic(wd, aWire);
        dic[p2] = wd;
        
        return success
        
    def removeWire(self, aWire):
        success = True;
        success = success and self._removeWire_coordDic(self.coordWireDict, aWire);
        success = success and self._removeWire_wireDic(self.wireDict, aWire);
        return success;
    
    
        
    def _addWire(self, wireDic, coordWireDic, aWire):
        self.wireDict[aWire.uuid] = aWire;
        p1 = aWire.getP1Tuple()
        p2 = aWire.getP2Tuple()
        
        if (p1 in self.coordWireDict) :
            dictWires = self.coordWireDict[p1];
        else :
            dictWires = {};
        dictWires[aWire.uuid] = aWire;
        self.coordWireDict[p1] = dictWires;
        
        if (p2 in self.coordWireDict) :
            dictWires = self.coordWireDict[p2];
        else :
            dictWires = {};
            
        dictWires[aWire.uuid] = aWire;
        self.coordWireDict[p2] = dictWires;
        return True;
    
    def addWire(self, aWire):
        return self._addWire(self.wireDict, self.coordWireDict, aWire);    
    
    def getAllWires(self):
        wires = [];
        wd = sorted(self.coordWireDict.items());
        for pp, dictWires in wd:
            wires.extend(list(sorted(dictWires.items())));
        return wires;
    
    def getWireDictAt(self, aPoint):
        if aPoint in self.coordWireDict:
            return self.coordWireDict[aPoint]
        return {};
    
    def getPinDictAt(self, aPoint):
        if aPoint in self.coordCompPinDict:
            return self.coordCompPinDict[aPoint];
        return {}
    
    def getWiresByCoord(self):
        return self.coordWireDict;
    
    def getJunctionCount(self, point):
        pp = point;
        cnt = 0;
        if (pp in self.coordCompPinDict):
            cnt = cnt+ len(self.coordCompPinDict[pp]);
        
        if (pp in self.coordWireDict):
            cnt = cnt+ len(self.coordWireDict[pp]); 

        return cnt;
        
    def wiresToPolyWires(self):
        changes = True
        cnt = 0;
        while changes :
            changes = False # assume no changes
            
            # create copies since we cannot change the dicts while iterating over them
            wireDictCpy = dict(self.wireDict);
            coordWireDictCpy = dict(self.coordWireDict)
            
            for coord, dictWires in coordWireDictCpy.items(): 
                isAtCompPin = (coord in self.coordCompPinDict);
                if (isAtCompPin): 
                    print(" Wire position "+str(coord)+' is incident with a component pin. Conversion to polywire suppressed.');
                
                if (len(dictWires) == 2) and (coord not in self.coordCompDict) and (not isAtCompPin): # two wires joined at this point and no component node there. convert to PolyWire
                    changes = True # we join two wires, thus change the set and must reprocess it
                    wires = list(dictWires.values());
                    
                    print('Joining wire1 = '+wires[0].asString()+' and wire2 = '+wires[1].asString()+' at '+str(coord)+'..');
                          
                    # create a new polywire
                    pwire = PolyWire.JoinWires(wires[0],wires[1]);
                    
                    #remove the wires from the lists
                    self._removeWire_coordDic(self.coordWireDict, wires[0])
                    self._removeWire_coordDic(self.coordWireDict, wires[1])
                    self._removeWire_wireDic(self.wireDict,wires[0])
                    self._removeWire_wireDic(self.wireDict,wires[1])
                    
                    # add the new wire
                    self._addWire(self.wireDict, self.coordWireDict, pwire);
                    cnt = cnt+1;
                    
                    print('.. joining resulted in polywire = '+pwire.asString()+'.');
                    
                    break; # break the loop. It could be that we also need to join the newly created polywire.
                
            #for uid, dictWires in self.wireDict:
            #    if len(dictWires) == 2: # two wires joined at this point: convert them into a PolyWire
    
        # no more changes
        print("Joining operations completed.")
        return cnt;

class Attribute:
    value = None;
    idnum = 0;
    optionlist = [];
    def __init__(self, kind, value):
        self.uuid = uuid.uuid4();
        self.value = value;
        self.x1rel = 0;
        self.y1rel = 0;
        self.x2rel = 0;
        self.y2rel = 0;
        self.visible = False;
        self.kind = kind;
        self.rot = 0;
        self.idnum = 0;
        self.size = 2;
        self.align = "Left";
        self.optionlist = [];
    
    def addOption(self, option):
        self.optionlist.append(option);

class SchObject:
    x1 = 0;
    y1 = 0;
    texx1 = 0;
    texy1 = 0;
    texrot = 0;
    texmirror = False;
    rotation = 0;
    mirror = False;
    symbol = None;
    circuitDict = None;
    value = 'UndefinedSchValue';
    _rounddigits=5;
    pathandctype = '';
    
    def __init__(self, ctype, x1, y1):
        self.x1 = x1;
        self.y1 = y1;
        self.uuid = uuid.uuid4();
        self.texx1 = 0;
        self.texy1 = 0;
        self.texrot = 0;
        self.texmirror = False;
        self.rotation = 0;
        self.mirror = False;
        self.value = "undefinedSchValue";
        self.symbol = None;
        self.circuitDict = None;
        self.path = '';
        self.pathandctype = '';
        self.value2 = ''
        self.attrlist = [];
        self._rounddigits=5; 
        
    def print(self):
        print(self.asString())
        
    def _latexEscape(self, text):
        """
            :param text: a plain text message
            :return: the message escaped to appear correctly in LaTeX
        """
        conv = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
            '\\': r'\textbackslash{}',
            '<': r'\textless',
            '>': r'\textgreater',
        }
        regex = re.compile('|'.join(re.escape((key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
        return regex.sub(lambda match: conv[match.group()], text)        
        
    def _coord2tex(self, pp):
        xscale = 1.0 * self.symbol.lt2tscale;
        yscale = -1.0 * self.symbol.lt2tscale; # y is inverse for LTspice files      
        
        xoffset = self.symbol.latexOriginX1;
        yoffset = self.symbol.latexOriginY1;
        
        pptex = (round(pp[0]*xscale+xoffset,self._rounddigits), round(pp[1]*yscale+yoffset, self._rounddigits))
        print('      new tex coord is '+str(pptex)+'.');
        
        return pptex;    
    
    def _coord2abs(self, coord):
        # preprocess
        pp = coord;
        mirror = self.mirror;
        if (self.symbol.latexOriginMirror):
            mirror = not mirror;        
        
        if (self.symbol.ckvUnsetOrFalse('suppressrotate')):
            # rotate
            rotdeg = (-1)*self.rotation + (-1)*self.symbol.latexOriginRot; # LTspice rotates CW positive, mathematics use CCW positive, therefore a minus sign.
            #if (mirror):
                #rotdeg = (-1)*rotdeg;
                #print ('      rotation reversed from '+str(-1*rotdeg)+'deg to '+str(rotdeg)+' due to mirroring.')
            
            pp = self.symbol.rotatePosOrigin(pp, rotdeg); 
            if (rotdeg != 0):
                print('      new '+str(rotdeg)+'deg rotated coord is '+str(pp)+'.');
        else:
            print('      possible rotation suppressed by conversion key-value pair')
    
            
        if (self.symbol.ckvUnsetOrFalse('suppressmirror')):
            # mirror
            if mirror:
                pp = ((-1)*pp[0], pp[1]) # mirror according to symbol origin        
                print('      new mirrored coord is '+str(pp)+'.');        
        else:
            print('      possible mirroring suppressed by conversion key-value pair')
            
            
        
        # convert to absolute
        ppabs = (pp[0] + self.x1,   pp[1] + self.y1); # move to absolute position according to our origin in absolute coordinates
        print('      new absolute coord is '+str(ppabs)+'.');
        return ppabs;    
    
    def _symcKVAttrStrToAttr(self, match):
        attr = match.group(1);
        res = self.symbol.conversionKV[attr]
        return str(res);    
    
    def _attrStrToAttr(self, match):
        attr = match.group(1);
        res = getattr(self, attr);
        return str(res);
        
    def _symAttrStrToAttr(self, match):
        attr = match.group(1);
        res = getattr(self.symbol, attr);
        return str(res);    
    
    def addAttribute(self, attrib):
        self.attrlist.append(attrib);
    
    def getAttributes(self, attrib):
        return self.attrlist;
    
    def getP1Tuple(self):
        return (self.x1, self.y1)
    
    def _checkRotatePM(self, match):
        rot = int(match.group(1))
        if (rot == 0):
            if (self.rotation == rot):
                return '1'
            else:
                return '-1'
            
        if (int((self.rotation/rot)%2) == 1):
            return '1';
        else:
            return '-1';
        
    def _checkRotateMP(self, match):
        rot = int(match.group(1))
        if (rot == 0):
            if (self.rotation == rot):
                return '-1'
            else:
                return '1'
            
        if (int((self.rotation/rot)%2) == 1):
            return '-1';
        else:
            return '1';
        
    def _checkRotate01(self, match):
        rot = int(match.group(1))
        if (rot == 0):
            if (self.rotation == rot):
                return '0'
            else:
                return '1'
        
        if (int((self.rotation/rot)%2) == 1):
            return '0';
        else:
            return '1';
        
    def _checkRotate10(self, match):
        rot = int(match.group(1))
        if (rot == 0):
            if (self.rotation == rot):
                return '1'
            else:
                return '0'
        
        if (int((self.rotation/rot)%2) == 1):
            return '1';
        else:
            return '0';
        
    def _checkLabelMirr(self, match):
        mirror = self._mirrored();
        rot = self.rotation;
        xy = match.group(1)
        res = '1'
        if (xy == 'x'):
            if ( (mirror and rot == 0) or (((rot/180)%2 == 1) and not mirror) ):
                res = '-1'
        elif (xy == 'y'):
            if ( ((rot == 90) or (rot == -270)) ):
                res = '-1'
        return res;
    
    def _mirrored(self):
        mirror = self.mirror;
        if (self.symbol.latexOriginMirror):
            mirror = not mirror;        
        if (self.symbol.symbolOriginMirror):
            mirror = not mirror;        
        return mirror;
    
    def _mirrorReplace(self, line, opt):
        mirror = self._mirrored();
           
        if (mirror):
            line = re.sub('##mirror_invert##','invert', line);
            line = re.sub('##mirror_mirror##','mirror', line);
            line = re.sub('##mirror_xscale##','xscale=-1', line);
            line = re.sub('##mirror_xscale_value##','-1', line);
            line = re.sub('##mirror_yscale##','yscale=-1', line);
            line = re.sub('##mirror_yscale_value##','-1', line);
            line = re.sub('##mirror##','invert', line); # for circuiTikz mirror means horizontal mirror, but we want vertical mirror, wich is invert in circuiTikz terminology
            if (int((self.rotation/90)%2) == 0): # not 90deg (or odd multiples) rotated
                line = re.sub('##mirror_rot_xscale_value##','-1', line); # rotated mirror scaling
                line = re.sub('##mirror_rot_yscale_value##','1', line); # rotated mirror scaling
            else:
                line = re.sub('##mirror_rot_xscale_value##','1', line); # normal mirror
                line = re.sub('##mirror_rot_yscale_value##','-1', line); # normal mirror
                
        else:
            line = re.sub('##mirror_invert##','', line);
            line = re.sub('##mirror_mirror##','', line);
            line = re.sub('##mirror_xscale##','', line);
            line = re.sub('##mirror_xscale_value##','1', line);
            line = re.sub('##mirror_yscale##','', line);
            line = re.sub('##mirror_yscale_value##','1', line);
            line = re.sub('##mirror##','', line); 
            
            line = re.sub('##mirror_rot_yscale_value##','1', line); # no mirror
            line = re.sub('##mirror_rot_xscale_value##','1', line); # no mirror
                 
        line = re.sub('##rotate_([-\d\.]+)_pmvalue##',self._checkRotatePM, line);
        line = re.sub('##rotate_([-\d\.]+)_mpvalue##',self._checkRotateMP, line);
        line = re.sub('##rotate_([-\d\.]+)_01value##',self._checkRotate01, line);
        line = re.sub('##rotate_([-\d\.]+)_10value##',self._checkRotate10, line);
        
        line = re.sub('##labelmirror([xy])##',self._checkLabelMirr, line);

        rotatemirror = 1;
        if (self.mirror):
            rotatemirror = -1;
        line = re.sub('##rotate_mirror##',str(round((-1)*self.rotation*rotatemirror+(-1)*self.symbol.latexOriginRot+(-1)*self.symbol.symbolOriginRot)), line);    
        
        return line;
    
    

class Component(SchObject):
    uuid = None;
    x1 = 0;
    y1 = 0;
    texx1 = 0;
    texy1 = 0;
    texrot = 0;
    texmirror = False;
    rotation = 0;
    mirror = False;
    ctype = "undefined";
    name = "undefined";
    kind = "undefined";
    value = "undefined";
    symbol = None;
    path = '';
    pathandctype = '';
    value2 = ""
    attrlist = [];
    
    def __init__(self, ctype, x1, y1, rot, mirror, name, value):
        super().__init__(ctype,x1,y1);
        self.ctype = ctype;
        self.x1 = x1;
        self.y1 = y1;
        self.texx1 = 0;
        self.texy1 = 0;
        self.rotation = rot;
        self.mirror = (mirror==True);
        self.symbol = None;
        self.path = '';
        self.pathandctype = '';
        self.value2 = ""
        self.attrlist = [];        
        
        self.circuitDict = None; # ref to parent circuit dict to determine junctions etc.
        self.pathandctype = ctype;
        re_ctype = re.compile(r'(.*\\\\)([a-zA-Z0-9_-]+)$', flags=re.IGNORECASE);
        m = re_ctype.match(self.pathandctype);
        if (m != None):
            self.path = m.group(1);
            self.path = self.path.replace('\\\\','\\');
            self.ctype = m.group(2);
        else:
            self.path = '';
            self.ctype = self.pathandctype;
        
        
        self.value = value;
        self.value2 = '';

        self.uuid = uuid.uuid4();
        
    def asString(self, indent=''):
        res = indent+'component "'+self.pathandctype+'" ('+self.path+','+self.ctype+') named "'+self.name+'" with value "'+self.value+'" at '+str((self.x1,self.y1))+' rot'+str(self.rotation)+' mirrored='+str(self.mirror)+'.\n';
        if (self.symbol != None):
            res = res + indent+'    '+'component symbol:'+self.symbol.asString(indent+'    ');
        return res;

    
    def _pinIsJunction(self, match):
        pinname = match.group(1);
        
        pin = self.symbol.latexPins.getPinByName(pinname);
        if (pin == None):
            pin = self.symbol.symbolPins.getPinByName(pinname);
        if (pin == None):
            print('Unable to find pin "'+pinname+'" of component '+self.pathandctype+' in either latex or asy pins. Using zero.');
            pp = (0, 0);
        else:
            pp = pin.getP1Tuple();
            
        # get incident wire count at point
        if (self.circuitDict == None):
            print('Unable to lookup pin Junction for pin "'+pinname+'" of component '+self.pathandctype+' in either latex or asy pins. Using no juncion.');
            return '';
        
        ppabs = self._coord2abs(pp);
        
        wdict = self.circuitDict.getWireDictAt(ppabs);
        
        cpindict = self.circuitDict.getPinDictAt(ppabs);
        cpindict.pop(self.uuid, None) # remove our own pin at this position
        
        if ((len(wdict) + len(cpindict)) >= 2): # more than two pins / wires at this point: junction
            return '*'
        else:
            return ''
    
    def getAbsolutePinPos(self, aPin):
        pp = aPin.getP1Tuple();
        ppabs = self._coord2abs(pp);
        return ppabs;
        
    def _pinToCoord(self, match):
        xscale = 1.0 * self.symbol.lt2tscale;
        yscale = -1.0 * self.symbol.lt2tscale; # y is inverse for LTspice files        
        mirror = self.mirror;
        
        if (self.symbol.latexOriginMirror):
            mirror = not mirror;
            
        pinname = match.group(1);
        pincoord = match.group(2);
        
        pin = self.symbol.latexPins.getPinByName(pinname);
        pin_src = 'asy2latex'
        
        if (pin == None):
            pin_src = 'asy'
            pin = self.symbol.symbolPins.getPinByName(pinname);
        if (pin == None):
            pin_src = 'none'
            print('Unable to find '+pin_src+' pin "'+pinname+'" of component '+self.pathandctype+' in either latex or asy pins. Using zero.');
            pp = (0, 0);
        else:
            pp = pin.getP1Tuple();
            
        print('    processing comp. "'+self.name+'" pin "'+pinname+'" at symbol coord '+str(pin.getP1Tuple())+':');
        
        # pp is relative to the component Origin
        ppabs = self._coord2abs(pp)
        
        pptex = self._coord2tex(ppabs);
        
        if (str.lower(pincoord) == 'x1'):
            res = str(pptex[0]);
        elif (str.lower(pincoord) == 'y1'):
            res = str(pptex[1]);
        else:
            print('Unknown pin coord component: "'+pincoord+'"');
            res = '??';
        
        return res;
    
    def _confAttrStrToAttr(self, match):
        attr = match.group(1);
        if (self.config.has_option('component',attr)):
            res = self.config.get('component',attr)
        else:
            res = '';
        return str(res);
    
    def _toLatexReplace(self, line, opt):
        # pattern, repl, string)
        line1 = line;
        
        line = re.sub('#([A-Za-z0-9_+\-!]+):([xy][0-9]+)#',self._pinToCoord, line);
        
        line = re.sub('#([A-Za-z0-9_+\-!]+):junction#',self._pinIsJunction, line);
        
        line = re.sub('#self.symbol.conversionKV.([A-Za-z0-9_\-!]+)#',self._symcKVAttrStrToAttr, line);
        
        line = re.sub('#self.symbol.([A-Za-z0-9_\-!]+)#',self._symAttrStrToAttr, line);
        
        line = re.sub('#self.config.([A-Za-z0-9_\-!]+)#',self._confAttrStrToAttr, line);
        
        line = re.sub('#self.([A-Za-z0-9_\-!]+)#',self._attrStrToAttr, line);
        
        
        
        line = re.sub('##options##',self.value2, line);
        
        line = re.sub('##rotate##',str(round((-1)*self.rotation+(-1)*self.symbol.latexOriginRot+(-1)*self.symbol.symbolOriginRot)), line);
        

        line = self._mirrorReplace(line, opt)
        
        
        print('Converted tex line "'+line1.replace('\n','')+'"\n'+
              ' to                "'+line.replace('\n','')+'"');
        
        return line;
        
    def translateToLatex(self, opt):
        if (opt == None):
            opt = {};
        
        p1 = (0,0);
        p1 = (p1[0] + self.symbol.symbolOriginX1, p1[1]+ self.symbol.symbolOriginY1);
        
        p1 = self._coord2abs(p1); # rotate and mirror origin offset
        
        lp= self._coord2tex(p1)
        
        self.texx1 = lp[0];
        self.texy1 = lp[1];
        
        self.texrot = self.rotation + (-1)*self.symbol.symbolOriginRot;
        self.texmirror = (self.mirror != self.symbol.symbolOriginMirror);
            
        print('Placing component '+self.ctype+' named "'+self.name+'" valued "'+self.value+'" at spice coord '+str(self.getP1Tuple())+', '+('M' if self.mirror else 'R')+str(self.rotation)+' -> tex '+str(self._coord2tex(self.getP1Tuple()))+'. ')
            
        translated = [];
            
        if (self.symbol != None):
            for line in self.symbol.latexTemplate:
                translated.append(self._toLatexReplace(line, opt));
            
        return translated;
    
    def setSymbolFromPrototype(self, aSymbolProto):
        # copy the symbol
        self.symbol = copy.deepcopy(aSymbolProto);
        
        # modify the symbol according to our properties

    
    def getPinList(self):
        return list(self.symbol.symbolPins.values());
    
    def addPin(self, aPin):
        self.symbol.symbolPins.addPin(aPin);
        
    def removePin(self,pinpos):
        self.symbol.symbolPins.removePin(aPin);
        
    def getPinCount(self):
        return len(self.symbol.symbolPins.getAllPins());
    
    def getPinPosList(self):
        return self.symbol.symbolPins.getAllPins()
    
    
    
class SchText(SchObject):
    def __init__(self, text, x1, y1):
        super().__init__('schtext', x1, y1);
        self.uuid = uuid.uuid4();
        self.text = text;
        self.x1 = x1;
        self.y1 = y1;
        self.size = 2;
        self.align = "Left"
        self.attrlist = [];
        self.symbol = None;
        
    def _toLatexReplace(self, line, opt):
        # pattern, repl, string)
        line1 = line;
        
        line = re.sub('#self.symbol.([A-Za-z0-9_\-!]+)#',self._symAttrStrToAttr, line);
        
        line = re.sub('#self.symbol.conversionKV.([A-Za-z0-9_\-!]+)#',self._symcKVAttrStrToAttr, line);
        
        line = re.sub('#self.textstr#',self._latexEscape(self.text), line);
        
        line = re.sub('#self.([A-Za-z0-9_\-!]+)#',self._attrStrToAttr, line);
        
        line = re.sub('##options##',self.symbol.value2, line);
        
        line = re.sub('##rotate##',str(round((-1)*self.rotation+(-1)*self.symbol.latexOriginRot+(-1)*self.symbol.symbolOriginRot)), line);
        
        line = self._mirrorReplace(line, opt);
        
        print('Converted tex line "'+line1.replace('\n','')+'"\n'+
              ' to                "'+line.replace('\n','')+'"');
        
        return line;
        
    def translateToLatex(self, opt):
        if (opt == None):
            opt = {};
        
        p1 = (0,0);
        p1 = (p1[0] + self.symbol.symbolOriginX1, p1[1]+ self.symbol.symbolOriginY1);
        
        p1 = self._coord2abs(p1); # rotate and mirror origin offset
        
        lp= self._coord2tex(p1)
        
        self.texx1 = lp[0];
        self.texy1 = lp[1];
        
        self.texrot = self.rotation + (-1)*self.symbol.symbolOriginRot;
        self.texmirror = (self.mirror != self.symbol.symbolOriginMirror);
            
        print('Placing text  '+self.pathandctype+' textcontent "'+self._latexEscape(self.text)+'" valued "'+self.value+'" at spice coord '+str(self.getP1Tuple())+', '+('M' if self.mirror else 'R')+str(self.rotation)+' -> tex '+str(self._coord2tex(self.getP1Tuple()))+'. ')
            
        translated = [];
            
        if (self.symbol != None):
            for line in self.symbol.latexTemplate:
                translated.append(self._toLatexReplace(line, opt));
            
        return translated;    
        

    
class NetLabel(SchObject):
    def __init__(self, label, x1, y1):
        super().__init__('netlabel', x1, y1);
        self.uuid = uuid.uuid4();
        self.label = label;
        self.x1 = x1;
        self.y1 = y1;
        self.attrlist = [];
        self.symbol = None;
        
    def _toLatexReplace(self, line, opt):
        # pattern, repl, string)
        line1 = line;
        
        line = re.sub('#self.symbol.([A-Za-z0-9_\-!]+)#',self._symAttrStrToAttr, line);
        
        line = re.sub('#self.symbol.conversionKV.([A-Za-z0-9_\-!]+)#',self._symcKVAttrStrToAttr, line);
        
        line = re.sub('#self.labelstr#',self._latexEscape(self.label), line);
        
        
        
        line = re.sub('#self.([A-Za-z0-9_\-!]+)#',self._attrStrToAttr, line);
        
        line = re.sub('##options##',self.symbol.value2, line);
        
        line = re.sub('##rotate##',str(round((-1)*self.rotation+(-1)*self.symbol.latexOriginRot+(-1)*self.symbol.symbolOriginRot)), line);
        
        line = self._mirrorReplace(line, opt);
        
        
        print('Converted tex line "'+line1.replace('\n','')+'"\n'+
              ' to                "'+line.replace('\n','')+'"');
        
        return line;
        
    def translateToLatex(self, opt):
        if (opt == None):
            opt = {};
        
        p1 = (0,0);
        p1 = (p1[0] + self.symbol.symbolOriginX1, p1[1]+ self.symbol.symbolOriginY1);
        
        p1 = self._coord2abs(p1); # rotate and mirror origin offset
        
        lp= self._coord2tex(p1)
        
        self.texx1 = lp[0];
        self.texy1 = lp[1];
        
        self.texrot = self.rotation + (-1)*self.symbol.symbolOriginRot;
        self.texmirror = (self.mirror != self.symbol.symbolOriginMirror);
            
        print('Placing label  '+self.pathandctype+' named "'+self._latexEscape(self.label)+'" valued "'+self.value+'" at spice coord '+str(self.getP1Tuple())+', '+('M' if self.mirror else 'R')+str(self.rotation)+' -> tex '+str(self._coord2tex(self.getP1Tuple()))+'. ')
            
        translated = [];
            
        if (self.symbol != None):
            for line in self.symbol.latexTemplate:
                translated.append(self._toLatexReplace(line, opt));
            
        return translated;    
    
    
    
class SchTwopoint(SchObject):
    def __init__(self, x1,y1, x2,y2, style):
        super().__init__('SchTwopoint_'+str(style),x1,y1);
        self.x1 = x1;
        self.y1 = y1;
        self.x2 = x2;
        self.y2 = y2;
        self.texx2 = 0; # texx1 inherited
        self.texy2 = 0;        
        self.texlinestyle = 'green,thick,dashed'
        self.kind = 'Normal';
        self.uuid = uuid.uuid4();
        self.style = style;
        self.name = '';
    def getP1Tuple(self):
        return (self.x1, self.y1);
    def getP2Tuple(self):
        return (self.x2, self.y2);
    
    def _toLatexReplace(self, line, opt):
        # pattern, repl, string)
        line1 = line;
        
        line = re.sub('#self.symbol.([A-Za-z0-9_\-!]+)#',self._symAttrStrToAttr, line);
        
        line = re.sub('#self.symbol.conversionKV.([A-Za-z0-9_\-!]+)#',self._symcKVAttrStrToAttr, line);
        
        #line = re.sub('#self.labelstr#',self._latexEscape(self.label), line);
        
        # ToDo: Linestyle
        
        line = re.sub('#self.([A-Za-z0-9_\-!]+)#',self._attrStrToAttr, line);
        
        line = re.sub('##options##',self.symbol.value2, line);
        
        line = re.sub('##rotate##',str(round((-1)*self.rotation+(-1)*self.symbol.latexOriginRot+(-1)*self.symbol.symbolOriginRot)), line);
        
        line = self._mirrorReplace(line, opt);
        
        
        print('Converted tex line "'+line1.replace('\n','')+'"\n'+
              ' to                "'+line.replace('\n','')+'"');
        
        return line;
        
    def translateToLatex(self, opt):
        if (opt == None):
            opt = {};
        
        p1 = (self.x1, self.y1);
        p2 = (self.x2, self.y2);
            
        lp1= self._coord2tex(p1)
        lp2= self._coord2tex(p2)
        
        self.texx1 = lp1[0];
        self.texy1 = lp1[1];
        
        self.texx2 = lp2[0];
        self.texy2 = lp2[1];
        
        linestyledict = {
            0 : 'lttotidrawcolor, solid',
            1 : 'lttotidrawcolor, line width=0.4pt, dashed',
            2 : 'lttotidrawcolor, line width=0.7pt, dotted',
            3 : 'lttotidrawcolor, line width=0.4pt, dashdotted',
            4 : 'lttotidrawcolor, line width=0.4pt, dashdotdotted', # \tikzstyle{dashdotdotted}=[dash pattern=on 3pt off 2pt on \the\pgflinewidth off 2pt on \the\pgflinewidth off 2pt]
            5 : 'lttotidrawcolor, line width=2pt, solid',
        }
        if self.style in linestyledict:
            self.texlinestyle = linestyledict[self.style];
        
        self.texrot = self.rotation + (-1)*self.symbol.symbolOriginRot;
        self.texmirror = (self.mirror != self.symbol.symbolOriginMirror);
            
        print('Placing SchTwoPoit  '+self.pathandctype+' at spice coord ['+str(self.getP1Tuple())+';'+str(self.getP2Tuple())+'], '+('M' if self.mirror else 'R')+str(self.rotation)+' -> tex ['+str(self._coord2tex(self.getP1Tuple()))+';'+str(self._coord2tex(self.getP2Tuple()))+']. ')
            
        translated = [];
            
        if (self.symbol != None):
            for line in self.symbol.latexTemplate:
                translated.append(self._toLatexReplace(line, opt));
            
        return translated;    

class SchLine(SchTwopoint):
    uuid = None;
    def __init__(self, x1, y1, x2, y2, style):
        super().__init__(x1,y1, x2,y2, style);
        self.pathandctype = 'SchLine'

    
class SchRect(SchTwopoint):
    uuid = None;
    def __init__(self, x1, y1, x2, y2, style):
        super().__init__(x1,y1, x2,y2, style);
        self.pathandctype = 'SchRect'
        
class SchCirc(SchTwopoint):
    uuid = None;
    def __init__(self, x1, y1, x2, y2, style):
        super().__init__(x1,y1, x2,y2, style);
        self.pathandctype = 'SchCirc'

class Wire:
    'LTpice Wire definition'
    name = "UnknownWire"
    
    wlen = 0;
    startjunction = False
    endjunction = False;
    x1 = float('NaN')
    y1 = float('NaN')
    x2 = float('NaN')
    y2 = float('NaN')

    def __init__(self, name, x1, y1, x2, y2):
        self.name = name
        self.x1 = x1;
        self.y1 = y1;
        self.x2 = x2;
        self.y2 = y2;
        self.uuid = uuid.uuid4();
        self.startjunction = False;
        self.endjunction = False;
    
    def getCoordTuple(self):
        ctuple = (self.x1, self.y1, self.x2, self.y2)
        return ctuple;
    def getP1Tuple(self):
        ctuple = (self.x1, self.y1)
        return ctuple;    
    def getP2Tuple(self):
        ctuple = (self.x2, self.y2)
        return ctuple;        
    
    def asString(self):
        line = 'wire: '+self.name+ ' = '+str(self.getP1Tuple())+' -> '+str(self.getP2Tuple())+'.';
        return(line);
    
    def asString2(self):
        return ("Wire : ", self.name,  ", x1=", str(self.x1), ", y1=", str(self.y1), " ;  x2=",str(self.x2),", y2=",str(self.y2),", startj:",str(self.startjunction),", endj:",str(self.endjunction),".")
    def print(self):
        print(self.asString);    
        
class PolyWire(Wire):
    # PolyWires only connect to other wires at p1=(x1,y1) and p2=(x2,y2), but have additional nodes xn, yn that determine their path between p1, p2
    #xn = [];
    #yn = [];
    
    def __init__(self, name, x1, y1, xn, yn, x2, y2):
        super().__init__(name, x1, y1, x2, y2);
        self.xn = xn
        self.yn = yn

        #Wire.__init__(name, x1, y1, x2, y2);
        
    @classmethod
    def JoinWires(cls, Wire1, Wire2):
        xn_ = [];
        yn_ = [];
        x1_ = 0; y1_ = 0;
        x2_ = 0; y2_ = 0;
        name_ = Wire1.name+"_"+Wire2.name 
        
        if (Wire1.getP1Tuple() == Wire2.getP1Tuple()):
            # joined at P1  back to back  Wire1 <-> Wire2
            print("  Wire1 <-> Wire2")
            x1_ = Wire1.x2
            y1_ = Wire1.y2
            
            if (type(Wire1) is PolyWire):
                an = list(Wire1.xn); # copy so we can reverse it if necessary
                an.reverse(); # turn the wire coordinate list 'around'
                xn_.extend(an); 
                an = list(Wire1.yn); # copy so we can reverse it if necessary
                an.reverse(); # turn the wire coordinate list 'around'
                yn_.extend(an);
            
            xn_.append(Wire1.x1)
            yn_.append(Wire1.y1)
            
            print("  (Wire1 complete..)")
            
            if (type(Wire2) is PolyWire):
                an = list(Wire2.xn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                xn_.extend(an); 
                an = list(Wire2.yn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                yn_.extend(an);            
            
            x2_ = Wire2.x2
            y2_ = Wire2.y2
        elif (Wire1.getP2Tuple() == Wire2.getP2Tuple()):
            # joined at P2 face to face  Wire1 >-< Wire2
            print("  Wire1 >-< Wire2")
            x1_ = Wire1.x1
            y1_ = Wire1.y1
        
            if (type(Wire1) is PolyWire):
                an = list(Wire1.xn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                xn_.extend(an); 
                an = list(Wire1.yn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                yn_.extend(an);
        
            xn_.append(Wire1.x2)
            yn_.append(Wire1.y2)
        
            if (type(Wire2) is PolyWire):
                an = list(Wire2.xn); # copy so we can reverse it if necessary
                an.reverse(); # turn the wire coordinate list 'around'
                xn_.extend(an); 
                an = list(Wire2.yn); # copy so we can reverse it if necessary
                an.reverse(); # turn the wire coordinate list 'around'
                yn_.extend(an);            
        
            x2_ = Wire2.x1
            y2_ = Wire2.y1            
        elif (Wire1.getP2Tuple() == Wire2.getP1Tuple()):
            # flow from Wire1 -> Wire2
            print("  Wire1 -> Wire2")
            x1_ = Wire1.x1
            y1_ = Wire1.y1
        
            if (type(Wire1) is PolyWire):
                an = list(Wire1.xn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                xn_.extend(an); 
                an = list(Wire1.yn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                yn_.extend(an);
        
            xn_.append(Wire1.x2)
            yn_.append(Wire1.y2)
        
            if (type(Wire2) is PolyWire):
                an = list(Wire2.xn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                xn_.extend(an); 
                an = list(Wire2.yn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                yn_.extend(an);            
        
            x2_ = Wire2.x2
            y2_ = Wire2.y2            
        elif (Wire1.getP1Tuple() == Wire2.getP2Tuple()):
            # flow from  Wire2 -> Wire1
            print("  Wire2 -> Wire1")
            x1_ = Wire2.x1
            y1_ = Wire2.y1            
            
            if (type(Wire2) is PolyWire):
                an = list(Wire2.xn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                xn_.extend(an); 
                an = list(Wire2.yn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                yn_.extend(an);                        
                
            xn_.append(Wire2.x2)
            yn_.append(Wire2.y2)            
            
            if (type(Wire1) is PolyWire):
                an = list(Wire1.xn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                xn_.extend(an); 
                an = list(Wire1.yn); # copy so we can reverse it if necessary
                #an.reverse(); # turn the wire coordinate list 'around'
                yn_.extend(an);
        
            x2_ = Wire1.x2
            y2_ = Wire1.y2            
        else:
            # unknown
            print("Error: Unknown wire configuration for PolyWire:JoinWires")
            
        print("  Constructing new wire object..")
            
        pw = cls(name_, x1_, y1_, xn_, yn_, x2_, y2_)
        return pw;
    
    def asString(self):
        line = 'polywire: '+self.name+ ' = '+str(self.getP1Tuple())+' -> '
        for i in range(0, len(self.xn)):
            pni = (self.xn[i], self.yn[i]);
            line = line + '['+ str(pni[0])+ ', '+str(pni[1])+']'+' -> ';
        line = line +str(self.getP2Tuple())+'.';
        return(line);    
    

class SymbolDict:
    def __init__(self):
        self.symbols = {};
        self.symbolsbypath = {};
        
    def hasSymbolName(self, aSymbolName):
        return aSymbolName in self.symbols;
    
    def hasSymbolPath(self, aSymbolNameandPath):
        return aSymbolNameandPath in self.symbolsbypath;    
        
    def addSymbol(self,aSymbol):
        self.symbols[aSymbol.ctype] = aSymbol;
        if (aSymbol.path != ""):
            spath = aSymbol.path +'\\';
        else:
            spath = '';
        self.symbolsbypath[spath+aSymbol.ctype] = aSymbol;
        
    def getSymbolByPath(self, aPath):
        if (aPath in self.symbolsbypath):
            aSymbol = self.symbolsbypath[aPath];
        else:
            aSymbol = None;
        return aSymbol;
    
    def getSymbolByCType(self, aCType):
        if (aCType in self.symbols):
            aSymbol = self.symbols[aCType];
        else:
            aSymbol = None;
        return aSymbol;
    
class SpatialDict:
    def __init__(self):
        self.objsbypos = dict();
        self.objsbyname = dict();
        self.objsbyid = dict();
        self.objsbyuuid = dict();
        self.objnameattrib = None;
        self.objposattrib = None;
        self.objidattrib = None;
        self.objuuidattrib = None;

    def _getField(self, aObj, aField):
        if ((aObj == None) or (aField == None)):
            return None; # todo: possibly throw an exception instead?
        
        objattrib = getattr(aObj, aField, None);
        if (objattrib == None):
            return None; # todo: possibly throw an exception instead?
        if (callable(objattrib)):
            pp = objattrib(); # requested attribute is a function. Use its value
        else:
            pp = objattrib; # requested attribute is a property. Use it directly.
        return pp;
    
    def _getPosAttrib(self, aObj):
        pp = None;
        if (type(self.objposattrib) is list): # every object has multiple positions
            pp = [];
            for posattrib in self.objposattrib:
                pp_ = self._getField(aObj, posattrib);
                pp.append(pp_)
        else:
            pp = [self._getField(aObj, self.objposattrib)];
        return pp;
    
    def _getSubidx(self, aObj):

        nn = self._getField(aObj, self.objnameattrib);
        ii = self._getField(aObj, self.objidattrib);
        uu = self._getField(aObj, self.objuuidattrib);
        subidx = None;
        if (uu != None):
            subidx = uu;                

        if (ii != None):
            subidx = ii;
        
        if (nn != None):
            subidx = nn; # hightest priority: last
        
        return subidx
    
    def addObj(self, aObj):

        pp = self._getPosAttrib(aObj);
        nn = self._getField(aObj, self.objnameattrib);
        ii = self._getField(aObj, self.objidattrib);
        uu = self._getField(aObj, self.objuuidattrib);
        
        subidx = self._getSubidx(aObj)

        if (ii != None):
            self.objsbyid[ii] = aObj;        
        
        if (nn != None):
            self.objsbyname[nn] = aObj;
        
        if (uu != None):
            self.objsbyuuid[uu] = aObj;
        
        if ((pp == None) or (subidx == None)):
            return False;
        
        for pp_ in pp:
            if pp_ in self.objsbypos:
                pdict = self.objsbypos[pp_];
                pdict[subidx] = aObj;
                self.objsbypos[pp_] = pdict;
            else:
                pdict = {};
                pdict[subidx] = aObj;
                self.objsbypos[pp_] = pdict;
    
    def getObjByName(self, aName):
        if (aName in self.objsbyname):
            return self.objsbyname[aName];
        else:
            return None;
    
    def getObjById(self, anId):
        if (anId in self.objsbyid):
            return self.objsbyid[anId];
        else:
            return None;
        
    def getObjsByPos(self, aPos):
        if (aPos in self.objsbypos):
            return self.objsbypos[aPos]
        else:
            return None;
        
    def getAllObjs(self):
        return list(self.objsbyid.items());
        
    def removeObj(self, aPin):
        pp = self._getPosAttrib(aObj);
        nn = self._getField(aObj, self.objnameattrib);
        ii = self._getField(aObj, self.objidattrib);
        uu = self._getField(aObj, self.objuuidattrib);
        
        subidx = self._getSubidx(aObj)
        
        self.objsbyname.pop(nn,None);
        
        self.objsbyid.pop(ii,None);
        
        self.objsbyuuid.pop(uu,None);
        
        for pp_ in pp:
            pdict = self.objsbypos.pop(pp_,None);
            if (pdict != None):
                pdict.pop(subidx,None);
                self.pinsbypos[pp_] = pdict; # add remaining objs at pos back
        
    def updateObj(self, aObj):
        self.removeObj(aObj);
        self.addObj(aObj);
    
class PinDict:
    def __init__(self):
        self.pinsbypos = dict();
        self.pinsbyname = dict();
        self.pinsbyorder = dict();
    
    def addPin(self, aPin):
        pp = aPin.getP1Tuple();
        self.pinsbyname[aPin.name] = aPin;
        self.pinsbyorder[aPin.order] = aPin;
        
        if pp in self.pinsbypos:
            pdict = self.pinsbypos[pp];
            pdict[aPin.name] = aPin;
            self.pinsbypos[pp] = pdict;
        else:
            pdict = {};
            pdict[aPin.name] = aPin;
            self.pinsbypos[pp] = pdict;
    
    def getPinByName(self, aPinName):
        if (aPinName in self.pinsbyname):
            return self.pinsbyname[aPinName];
        else:
            return None;
    
    def getPinByOrder(self, aPinOrder):
        if (aPinOrder in self.pinsbyorder):
            return self.pinsbyorder[aPinOrder];
        else:
            return None;
        
    def getPinByPos(self, aPinPos):
        if (aPinPos in self.pinsbypos):
            return self.pinsbypos[aPinPos]
        else:
            return None;
        
    def getAllPins(self):
        return list(self.pinsbyname.items());
        
    def removePin(self, aPin):
        self.pinsbyname.pop(aPin.name,None);
        pp = aPin.getP1Tuple();
        pdict = self.pinsbypos.pop(pp,None);
        if (pdict != None):
            pdict.pop(aPin.name,None);
            self.pinsbypos[pp] = pdict; # add remaining pins at pos back
        
        self.pinsbyorder.pop(aPin.order,None);
        
    def updatePin(self, aPin):
        pp = aPin.getP1Tuple();
        self.pinsbyname[aPin.name] = aPin;
        self.pinsbyorder[aPin.order] = aPin;
        
        if pp in self.pinsbypos:
            pdict = self.pinsbypos[pp];
            pdict[aPin.name] = aPin;
            self.pinsbypos[pp] = pdict;
        else:
            pdict = {};
            pdict[aPin.name] = aPin;
            self.pinsbypos[pp] = pdict;
    
    
class Symbol:
    
    def __init__(self, stype):
        self.symboltype = stype;
        self.ctype = ''; # the component ctype for this symbol
        self.prefix = '';
        self.description = '';
        self.value = ''
        self.value2 = ''
        self.attributes = dict();
        self.x1 = 0;
        self.y1 = 0;
        self.path = '';
        self.pathandctype = '';
        self.symbolPins = PinDict();
        self.conversionKV = {} # key=value dict for conversion options from asy2tex file
        self.latexPins = PinDict();
        self.latexOriginX1 = 0;
        self.latexOriginY1 = 0;
        self.latexOriginRot = 0;
        self.latexOriginMirror = False;
        self.symbolOriginX1 = 0;
        self.symbolOriginY1 = 0;
        self.symbolOriginRot = 0;
        self.symbolOriginMirror = False;        
        self.latexElementName = '';
        self.latexType = 'Node';
        self.latexTemplate = []; # list of lines with latex code with  #PinName:x1# coordinate and ##options## placeholder 
        
        self.lt2tscale = None;
        
    def addPin(self, aPin):
        self.symbolPins.addPin(aPin);
    
    def rotatePos(self, aPos, rotDeg, aOrigin):
        x1=aPos[0]-aOrigin[0];
        y1=aPos[1]-aOrigin[1];
        rotRad = rotDeg*math.pi/180.0;
        
        x2 = x1*math.cos(rotRad) + y1*math.sin(rotRad);
        y2 = x1*(-1.0)*math.sin(rotRad) + y1*math.cos(rotRad);
        
        x2 = x2+aOrigin[0];
        y2 = y2+aOrigin[1];
        return (x2, y2);
    
    def rotatePosOrigin(self, aPos, rotDeg):
        return self.rotatePos(aPos,rotDeg, (0.0,0.0));    

    def rotatePosInt(self, aPos, rotDeg, aOrigin):
        pp = self.rotatePos(aPos,rotDeg,aOrigin);
        x2 = round(pp[0]);
        y2 = round(pp[1]);
        return (x2, y2);
    
    def rotatePosIntOrigin(self, aPos, rotDeg):
        return self.rotatePosInt(aPos,rotDeg, (0,0));
    
    def ckvUnsetOrFalse(self, key):
        if not (key in self.conversionKV):
            return True;
        res = (str.lower(self.conversionKV[key]) == 'false') or ( (self.conversionKV[key]) == '0' )
        return res;
        
    def ckvUnsetOrTrue(self, key):
        if not (key in self.conversionKV):
            return True;
        res = (str.lower(self.conversionKV[key]) == 'true') or ( (self.conversionKV[key]) == '1' )    
        return res;

    def ckvSetAndFalse(self, key):
        if not (key in self.conversionKV):
            return False;
        res = (str.lower(self.conversionKV[key]) == 'false') or ( (self.conversionKV[key]) == '0' )
        return res;
        
    def ckvSetAndTrue(self, key):
        if not (key in self.conversionKV):
            return False;
        res = (str.lower(self.conversionKV[key]) == 'true') or ( (self.conversionKV[key]) == '1' )    
        return res;
    
    def asString(self, indent=''):
        res = indent+'Symbol "'+self.ctype+'" at path "'+self.path+'" with prefix "'+self.prefix+'" ';
        res = res+'at origin '+str((self.x1,self.y1))+'.\n'
        for pname, pin in self.symbolPins.getAllPins():
            res = res + pin.asString(indent+'    ');
        return res;
    
class SymPin:
    def __init__(self):
        self.name = '';
        self.x1 = 0;
        self.y1 = 0;
        self.labelpos = 'NONE';
        self.labeloffset = 8;
        self.order = -1;
        self.rot = 0;
        self.length = 0;

    def getP1Tuple(self):
        ctuple = (self.x1, self.y1)
        return ctuple;    
    
    def asString(self, indent=''):
        res = indent+ 'Pin "'+self.name+'" ord '+str(self.order)+' at '+str(self.getP1Tuple())+' rot='+str(self.rot)+' len='+str(self.length)+'.\n';
        return res;

from argparse import ArgumentParser

def main():
    parser = ArgumentParser('Converts asc files into circuiTikz tex files. Takes the asc file as an argument.')
    parser.add_argument("file")
    args = parser.parse_args()
    
    l2tobj = lt2circuiTikz();
    l2tobj.readASCFile(args.file);
    l2tobj.writeCircuiTikz(args.file+'.tex');    
    


isstandalone = False;
try:
    approot = os.path.dirname(os.path.abspath(__file__))
    if __name__ == '__main__':
        isstandalone = True;        
except NameError:  # We are the main py2exe script, not a module
    import sys
    approot = os.path.dirname(os.path.abspath(sys.argv[0]))
    isstandalone = True;   
    
if (isstandalone):
    main();
