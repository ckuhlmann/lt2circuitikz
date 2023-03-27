python dev_lt2ti.py>dev_lt2ti.log

powershell -command "Get-Content dev_lt2ti.log -Tail 2"

choice /C YN /T 5 /D Y /M "Continue with latex compile? (Yes in 5 sec)"
if errorlevel 2 goto CloseCMD

cd .\examples\
call .\compile_dev.bat
cd ..
goto CloseCMD


:CloseCMD
rem pause

choice /C YN /T 30 /D Y /M "Translate: CLose console window? (Yes in 30 sec)"
if NOT errorlevel 2 goto EOF
pause


:EOF