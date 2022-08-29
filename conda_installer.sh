echo " ################################################# "
echo " #   simplified DUI2 installer for developers    # "
echo " ################################################# "
echo " "
echo " Downloading Miniconda3 "
echo " "
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
echo " "
echo " Installing Miniconda3"
echo " "
bash Miniconda3-latest-Linux-x86_64.sh -b
bash ~/miniconda3/etc/profile.d/conda.sh
~/miniconda3/bin/conda init bash
