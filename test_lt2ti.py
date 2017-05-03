import lt2ti;

#fn = r'examples\TestTransistors.asc';
fn = r'examples\Test.asc';
l2tobj = lt2ti.lt2circuiTikz();
l2tobj.readASCFile(fn);
l2tobj.writeCircuiTikz(fn+r'.tex');