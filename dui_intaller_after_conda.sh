echo " ################################################# "
echo " #   simplified DUI2 installer for developers    # "
echo " ################################################# "
echo " "
echo " installing git "
echo " "
conda install -c conda-forge git -y
echo " "
echo " installing dials "
echo " "
conda install -c conda-forge dials -y
echo " "
echo " installing DUI2 dependency PySide2  "
echo " "
conda install -c conda-forge pyside2 -y
echo " "
echo " cloning DUI2 code "
echo " "
git clone -b v2023.11.13  https://github.com/ccp4/DUI2.git
L_DIR="$(pwd "$0")"
echo " "
echo "run: \"python $L_DIR/DUI2/src/all_local.py\" to launch DUI2 locally"
echo " "
