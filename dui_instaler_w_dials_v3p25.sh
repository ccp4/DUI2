mkdir -p $1
cd $1
INI_DIR_PATH=$(pwd)
printf "\n\n Downloading Dials \n\n"
wget https://github.com/dials/dials/releases/download/v3.25.0/dials-v3-25-0-linux-x86_64.tar.xz
printf "\n\n Decompressing  Dials \n\n"
tar -xf dials-v3-25-0-linux-x86_64.tar.xz
cd $INI_DIR_PATH/dials-installer/
printf "\n\n Installing Dials \n\n"
./install --prefix $INI_DIR_PATH
source $INI_DIR_PATH/dials-v3-25-0/dials_env.sh
printf "\n\n Installing dependency: PySide6 \n\n"
dials.python -m pip install pyside6
cd $INI_DIR_PATH/
printf "\n\n Downloading Dui2 with git \n\n"
git clone -b v2025.12.5  https://github.com/ccp4/DUI2.git
printf "\n\n Done \n\n"
printf "\n\n You should type:\n\n"
printf "   source $INI_DIR_PATH/dials-v3-25-0/dials_env.sh  "
printf "\n\n Then: \n\n"
printf "   dials.python $INI_DIR_PATH/DUI2/src/run_dui2.py \n\n"
printf "to run Dui2 \n\n"

