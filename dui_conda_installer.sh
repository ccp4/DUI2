echo " ################################################# "
echo " #   simplified DUI2 installer for developers    # "
echo " ################################################# "
echo " "
echo " installing git "
conda install -c conda-forge git -y
echo " installing dials "
conda install -c conda-forge dials -y
echo " installing DUI2 dependency PySide2  "
conda install -c conda-forge pyside2 -y
echo " Downloading DUI2 code "
git clone https://github.com/ccp4/DUI2.git
L_DIR="$(pwd "$0")"
echo " "
echo "run: \"python $L_DIR/DUI2/src/all_local.py\" to launch DUI2 locally"
echo " "
