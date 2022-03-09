echo " *************************************** "
echo " *                                     * "
echo " *         INSTALLING DIALS v3.8.3     * "
echo " *                                     * "
echo " *************************************** "
INI_DIR_PATH=$(pwd)
mkdir dials_installer_tmp
cd dials_installer_tmp
wget https://github.com/dials/dials/releases/download/v3.8.3/dials-v3-8-3-linux-x86_64.tar.xz
tar -xvf dials-v3-8-3-linux-x86_64.tar.xz
cd dials-installer
./install --prefix=$INI_DIR_PATH
echo " *************************************** "
echo " *                                     * "
echo " *         INSTALLING DUI2 DEPS        * "
echo " *                                     * "
echo " *************************************** "
cd $INI_DIR_PATH
source dials-v3-8-3/dials_env.sh
libtbx.conda install pyside2 -y
libtbx.conda install git -y
###################### libtbx.conda install -c conda-forge gxx does not seems to work
echo " *************************************** "
echo " *                                     * "
echo " *         INSTALLING DUI2             * "
echo " *                                     * "
echo " *************************************** "
git clone https://github.com/ccp4/DUI2.git
cd DUI2/src/server/img_uploader/
dials.python compyling_boost_ext.py
echo " *************************************** "
echo " *                                     * "
echo " *         DIALS and DUI2 READY        * "
echo " *                                     * "
echo " *************************************** "
