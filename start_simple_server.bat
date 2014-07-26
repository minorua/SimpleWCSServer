@echo off
set o4w_root=C:\OSGeo4W64
set o4w_env=%o4w_root%\bin\o4w_env.bat

if exist %o4w_env% (
call %o4w_env%
python wcs.py
) else (
echo %o4w_env% not exists.
echo Edit the path in start_simple_server.bat.
)
pause
