printf "=========================================\n"
printf "#          INSTALLING DIALS v3.8.3      #\n"
printf "=========================================\n\n"
INI_DIR_PATH=$(pwd)
mkdir dials_installer_tmp
cd dials_installer_tmp
wget https://github.com/dials/dials/releases/download/v3.8.3/dials-v3-8-3-linux-x86_64.tar.xz
tar -xvf dials-v3-8-3-linux-x86_64.tar.xz
cd dials-installer
./install --prefix=$INI_DIR_PATH
printf "=========================================\n"
printf "#          INSTALLING DUI2 DEPS         #\n"
printf "=========================================\n\n"
cd $INI_DIR_PATH
source dials-v3-8-3/dials_env.sh
libtbx.conda install pyside2 -y
libtbx.conda install git -y
###################### libtbx.conda install -c conda-forge gxx does not seems to work
printf "=========================================\n"
printf "#          INSTALLING DUI2              #\n"
printf "=========================================\n\n"
git clone https://github.com/ccp4/DUI2.git
cd DUI2/src/server/img_uploader/
dials.python compyling_boost_ext.py > compyling_ext.log
printf "=========================================\n"
printf "#          DIALS and DUI2 INSTALLED     #\n"
printf "=========================================\n\n"
cd $INI_DIR_PATH
rm -rf dials_installer_tmp/
printf "Setting up launchers ...\n"
mkdir dui_cmd_tools
cd dui_cmd_tools
CMD_TOOLS_PATH=$(pwd)
SET_DIALS_ENV="source $INI_DIR_PATH/dials-v3-8-3/dials_env.sh"
CLIENT_EXE_CMD="dials.python $INI_DIR_PATH/DUI2/src/client/main_client.py \$\@"
echo $SET_DIALS_ENV > dui_client
echo $CLIENT_EXE_CMD >> dui_client
chmod +x dui_client
SERVER_EXE_CMD="dials.python $INI_DIR_PATH/DUI2/src/server/main_server.py \$\@"
echo $SET_DIALS_ENV > dui_server
echo $SERVER_EXE_CMD >> dui_server
chmod +x dui_server
printf " ... Done\n\n"
printf "=========================================\n"
printf "#          DIALS and DUI2 READY         #\n"
printf "=========================================\n\n\n\n"
printf "To set enviromet to run DUI2(including Dials) type:\n\n"
printf "  export PATH=$CMD_TOOLS_PATH:\$PATH  \n\n"
printf "or add it to your init bash shell\n\n"
cd $INI_DIR_PATH
