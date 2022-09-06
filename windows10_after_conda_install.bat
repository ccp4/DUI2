call conda install -c conda-forge git -y
call conda install -c conda-forge dials -y
call conda install -c conda-forge pyside2 -y
git clone https://github.com/ccp4/DUI2.git
set ini_dir=%cd%
set full_sting=python %ini_dir%\DUI2\src\all_local.py windows_exe=true
echo %full_sting% > dui_all_local.bat
echo use the dui_all_local.bat script to launch Dui2
