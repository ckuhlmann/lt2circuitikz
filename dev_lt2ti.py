import lt2ti;
import os;

#fn = r'examples\TestTransistors.asc';
#fn = r'examples\Test.asc';
fn = r'examples'+os.sep+'dev.asc';
#fn = r'examples\Draft2.asc'; # lines and rects
#fn = r'examples\Draft3.asc'; # lines and rects
#fn = r'examples\InductorEC.asc'; # lines and rects
l2tobj = lt2ti.lt2circuiTikz();
l2tobj.readASCFile(fn);
l2tobj.writeCircuiTikz(fn+r'.tex');