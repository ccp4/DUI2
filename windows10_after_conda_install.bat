conda install -c conda-forge git -y && ^
conda install -c conda-forge dials -y && ^
conda install -c conda-forge pyside2 -y && ^
git clone https://github.com/ccp4/DUI2.git && ^
set ini_dir=%cd%
set full_sting=python %ini_dir%\src\all_local.py windows_exe=true
echo %full_sting% > dui_all_local.bat
echo use the dui_all_local.bat script to launch Dui2
