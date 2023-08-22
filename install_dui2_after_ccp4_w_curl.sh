mkdir dui_install
cd dui_install
INI_DIR_PATH=$(pwd)
printf "========================================\n"
printf "#           DOWNLOADING DUI2           #\n"
printf "========================================\n\n"
TAG_VER="0.999.7"
TO_CURL="https://github.com/ccp4/DUI2/archive/refs/tags/v$TAG_VER.zip"
curl -L -O $TO_CURL
printf "========================================\n"
printf "#       DUI2 DOWNLOADED (as .zip)      #\n"
printf "========================================\n\n"
mv "v$TAG_VER.zip" DUI2.zip
unzip DUI2.zip
rm DUI2.zip
printf "========================================\n"
printf "  Done   \n"
printf "========================================\n\n"
printf "Setting up launchers ...\n"
mkdir dui_cmd_tools
cd dui_cmd_tools
CMD_TOOLS_PATH=$(pwd)

EXPORT_CMD="export QTWEBENGINE_DISABLE_SANDBOX=1"

CLIENT_EXE_CMD="dials.python $INI_DIR_PATH/DUI2-$TAG_VER/src/only_client.py \$@"
echo $EXPORT_CMD$'\n'$CLIENT_EXE_CMD > dui_client
chmod +x dui_client

SERVER_EXE_CMD="dials.python $INI_DIR_PATH/DUI2-$TAG_VER/src/only_server.py \$@"
echo $SERVER_EXE_CMD > dui_server
chmod +x dui_server

ALL_LOCAL_CMD="dials.python $INI_DIR_PATH/DUI2-$TAG_VER/src/all_local.py \$@"
echo $EXPORT_CMD$'\n'$ALL_LOCAL_CMD > dui_all_local
chmod +x dui_all_local

printf " ... Done\n\n"
printf "========================================\n"
printf "#               DUI2 READY             #\n"
printf "========================================\n\n"
printf " commands abailable: \n\n"
printf "   dui_all_local,  dui_server,  dui_client\n\n"
printf " To set enviromet to run DUI2 (including Dials) type:\n\n"
printf "   export PATH=$CMD_TOOLS_PATH:\$PATH  \n\n"
printf " or add it to your init bash shell\n\n"
cd $INI_DIR_PATH
cd ..


