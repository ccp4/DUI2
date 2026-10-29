mkdir -p $1
cd $1
INI_DIR_PATH=$(pwd)
printf "\n\n Downloading Dials \n\n"
wget https://github.com/dials/dials/releases/download/v3.30.1/DIALS-3.30.1-Linux-x86_64.sh
printf "\n\n Installing Dials \n\n"
chmod +x DIALS-3.30.1-Linux-x86_64.sh
./DIALS-3.30.1-Linux-x86_64.sh -p$INI_DIR_PATH/dials_w_pyside -b -m
printf "\n\n Installing dependency: PySide6 \n\n"
$INI_DIR_PATH/dials_w_pyside/bin/python -m pip install pyside6
cd $INI_DIR_PATH/
printf "\n\n Downloading Dui2 with git \n\n"
git clone -b v2026.9.21  https://github.com/ccp4/DUI2.git
printf "\n\n Done \n\n"
printf "=================================================================================="
printf "\n\n You should type:\n\n"
printf "   source $INI_DIR_PATH/dials_w_pyside/setpaths.sh   "
printf "\n\n Then: \n\n"
printf "   $INI_DIR_PATH/dials_w_pyside/bin/python $INI_DIR_PATH/DUI2/src/run_dui2.py \n\n"
printf "to run Dui2 \n\n"

