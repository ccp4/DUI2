echo "========================================="
echo "#          INSTALLING DIALS v3.8.3      #"
echo "========================================="
INI_DIR_PATH=$(pwd)
mkdir dials_installer_tmp
cd dials_installer_tmp
wget https://github.com/dials/dials/releases/download/v3.8.3/dials-v3-8-3-linux-x86_64.tar.xz
tar -xvf dials-v3-8-3-linux-x86_64.tar.xz
cd dials-installer
./install --prefix=$INI_DIR_PATH
echo "========================================="
echo "#          INSTALLING DUI2 DEPS         #"
echo "========================================="
cd $INI_DIR_PATH
source dials-v3-8-3/dials_env.sh
libtbx.conda install pyside2 -y
libtbx.conda install git -y
###################### libtbx.conda install -c conda-forge gxx does not seems to work
echo "========================================="
echo "#          INSTALLING DUI2              #"
echo "========================================="
git clone https://github.com/ccp4/DUI2.git
cd DUI2/src/server/img_uploader/
dials.python compyling_boost_ext.py
echo "========================================="
echo "#          DIALS and DUI2 INSTALLED     #"
echo "========================================="
cd $INI_DIR_PATH
rm -rf dials_installer_tmp/
CLIENT_EXE_CMD="dials.python $INI_DIR_PATH/DUI2/src/client/main_client.py"
echo $CLIENT_EXE_CMD > dui_client
chmod +x dui_client
SERVER_EXE_CMD="dials.python $INI_DIR_PATH/DUI2/src/server/main_server.py"
echo $SERVER_EXE_CMD > dui_server
chmod +x dui_server
echo "========================================="
echo "#          DIALS and DUI2 READY         #"
echo "========================================="
