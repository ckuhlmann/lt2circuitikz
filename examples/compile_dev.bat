pdflatex dev.asc.tex


choice /C YN /T 30 /D Y /M "Compile: CLose console window? (Yes in 30 sec)"
if NOT errorlevel 2 goto EOF
pause


:EOF