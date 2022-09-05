ECHO ####################################################
ECHO Installer of Dui2 starting from a Conda installation
ECHO ####################################################
ECHO Installing git
conda install -c conda-forge git -y && ^
ECHO Installing dials
conda install -c conda-forge dials -y && ^
ECHO Installing PySide2
conda install -c conda-forge pyside2 -y && ^
ECHO cloning Dui2 source code
git clone https://github.com/ccp4/DUI2.git
ECHO done
