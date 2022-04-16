mkdir dials_n_dui_installs
cd dials_n_dui_installs
printf "========================================\n"
printf "#        INSTALLING DIALS v3.9.0       #\n"
printf "========================================\n\n"
INI_DIR_PATH=$(pwd)
mkdir dials_installer_tmp
cd dials_installer_tmp
wget https://github.com/dials/dials/releases/download/v3.9.0/dials-v3-9-0-linux-x86_64.tar.xz
printf "decompressing the dials installer, this might take a few minutes ... \n\n"
tar -xf dials-v3-9-0-linux-x86_64.tar.xz
cd dials-installer
./install --prefix=$INI_DIR_PATH
cd $INI_DIR_PATH
source dials-v3-9-0/dials_env.sh
printf "========================================\n"
printf "#           INSTALLING MAMBA           #\n"
printf "========================================\n\n"
libtbx.conda install -c conda-forge mamba -y
printf "Setting up mamba ...\n"
libtbx.refresh
printf "========================================\n"
printf "#         INSTALLING DUI2 DEPS         #\n"
printf "========================================\n\n"
libtbx.mamba install pyside2 -y
libtbx.mamba install git -y
printf "========================================\n"
printf "#           INSTALLING DUI2            #\n"
printf "========================================\n\n"
git clone https://github.com/ccp4/DUI2.git
cd DUI2/src/server/img_uploader/
printf "========================================\n"
printf "#     COMPYLING DUI2 C++ EXTENSION     #\n"
printf "========================================\n\n"
dials.python compyling_boost_ext.py
printf "========================================\n"
printf "#       DIALS and DUI2 INSTALLED       #\n"
printf "========================================\n\n"
cd $INI_DIR_PATH
rm -rf dials_installer_tmp/
printf "Setting up launchers ...\n"
mkdir dui_cmd_tools
cd dui_cmd_tools

CMD_TOOLS_PATH=$(pwd)

SET_DIALS_ENV="source $INI_DIR_PATH/dials-v3-9-0/dials_env.sh"
SET_W_ENG_FLAG="export QTWEBENGINE_CHROMIUM_FLAGS=\"--no-sandbox\""

CLIENT_EXE_CMD="dials.python $INI_DIR_PATH/DUI2/src/client/main_client.py \$@"
echo $SET_W_ENG_FLAG > dui_client
echo $SET_DIALS_ENV >> dui_client
echo $CLIENT_EXE_CMD >> dui_client
chmod +x dui_client

SERVER_EXE_CMD="dials.python $INI_DIR_PATH/DUI2/src/server/main_server.py \$@"
echo $SET_W_ENG_FLAG > dui_server
echo $SET_DIALS_ENV >> dui_server
echo $SERVER_EXE_CMD >> dui_server
chmod +x dui_server

ALL_LOCAL_CMD_N1="dui_server all_local=true &"
ALL_LOCAL_CMD_N2="dui_client all_local=true"
echo $ALL_LOCAL_CMD_N1 > dui_all_local
echo $ALL_LOCAL_CMD_N2 >> dui_all_local
chmod +x dui_all_local

printf " ... Done\n\n"
printf "========================================\n"
printf "#         DIALS and DUI2 READY         #\n"
printf "========================================\n\n"
printf "To set enviromet to run DUI2 (including Dials) type:\n\n"
printf "  export PATH=$CMD_TOOLS_PATH:\$PATH  \n\n"
printf "or add it to your init bash shell\n\n"

cd $INI_DIR_PATH
cd ..
