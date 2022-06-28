mkdir dui_dev
cd dui_dev
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
libtbx.conda update -n base conda -y

libtbx.refresh
printf "========================================\n"
printf "#         INSTALLING DUI2 DEPS         #\n"
printf "========================================\n\n"
libtbx.conda install -c conda-forge pyside2 -y
printf "========================================\n"
printf "#           INSTALLING DUI2            #\n"
printf "========================================\n\n"

{ # try
    git clone https://github.com/ccp4/DUI2.git &&
    printf "  GIT use  \n\n "
} || { # except
    wget https://github.com/ccp4/DUI2/archive/refs/heads/master.zip
    unzip master.zip
    mv DUI2-master DUI2
    rm master.zip
    printf "  using WGET intead of GIT  \n\n "
}

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

CLIENT_EXE_CMD="dials.python $INI_DIR_PATH/DUI2/src/only_client.py \$@"
echo $SET_W_ENG_FLAG > dui_client
echo $SET_DIALS_ENV >> dui_client
echo $CLIENT_EXE_CMD >> dui_client
chmod +x dui_client

SERVER_EXE_CMD="dials.python $INI_DIR_PATH/DUI2/src/only_server.py \$@"
echo $SET_W_ENG_FLAG > dui_server
echo $SET_DIALS_ENV >> dui_server
echo $SERVER_EXE_CMD >> dui_server
chmod +x dui_server

ALL_LOCAL_CMD="dials.python $INI_DIR_PATH/DUI2/src/all_local.py \$@"
echo $SET_W_ENG_FLAG > dui_all_local
echo $SET_DIALS_ENV >> dui_all_local
echo $ALL_LOCAL_CMD >> dui_all_local

chmod +x dui_all_local

printf " ... Done\n\n"
printf "========================================\n"
printf "#         DIALS and DUI2 READY         #\n"
printf "========================================\n\n"
printf "\n\n If the HTML report crashes, try running the following command:\n\n  "
printf "cp /usr/lib/x86_64-linux-gnu/libstdc++.so.6 $INI_DIR_PATH/dials-v3-9-0/conda_base/lib/\n\n"
printf "   or (depending of your linux distro)  \n\n  "
printf "cp /usr/lib64/libstdc++.so.6 $INI_DIR_PATH/dials-v3-9-0/conda_base/lib/\n\n"
printf " commands available: \n\n"
printf "   dui_all_local,  dui_server,  dui_client\n\n"
printf " To set enviromet to run DUI2 (including Dials) type:\n\n"
printf "   export PATH=$CMD_TOOLS_PATH:\$PATH  \n\n"
printf " or add it to your init bash shell\n\n"

cd $INI_DIR_PATH
cd ..
