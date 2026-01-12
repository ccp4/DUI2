# DUI2

client/server implementation of DUI (Dials User Interface)

## Requirements for installing the latest version of DUI2

It's worth noting that DUI2 comes pre-installed with CCP4. The project depends on a working installation of `python3` along with several key packages, including `dials`, `pyside2` or `pyside3`, and `requests`, among others. There are three main ways to install the latest version of DUI2:

## Option 1, Installation with curl and ccp4

This assumes you have already installed and set up CCP4, which include `dials` and `pyside2`.

First download install script for `DUI2`:

      curl -L -O https://raw.githubusercontent.com/ccp4/DUI2/master/install_dui2_after_ccp4_w_curl.sh

Next run the downloaded script with `bash`:

      bash install_dui2_after_ccp4_w_curl.sh

Follow the instruction at the end of the script.

There are three available command line tools after installation:

1. Fully local App (running both, server and client locally)

       dui2

2. Server App (Which actually runs Dials commands)

       dui2_server_side host=MY_HOST port=MY_PORT init_path=/PATH/TO/USER/DATA

3. Client App (GUI front end that talks to the Server App)

       dui2_client_app url=http://...[URL of the server]

## Option 2, Installation of everything (including Dials) with conda, mamba and git

This assumes you have already installed an Anaconda package manger like `miniconda` and have a BASH shell active with the `conda` command enabled, see https://docs.anaconda.com/miniconda/install/ for details.

First update `conda`:

       conda update conda -y

We will use `mamba` to make the installation of `Dials` and other needed dependencies in a virtual environment easier and faster:

       conda install -c=conda-forge mamba -y

Provably Anaconda will ask you to run a specific command or to close and reopen your shell to make the installation of `mamba` effective

Next create a virtual environment with `Dials`, `PySide V2`, `PyQt webengine` and `git` inside it, replace `/PATH/TO/ENV/W/NAME` with the path where you want to install `Dials` and the GUI dependencies. This may take a few minutes:

       mamba create -p /PATH/TO/ENV/W/NAME -c conda-forge python=3.11 dials pyside2 pyqtwebengine git

Now we should activate our newly created environment, again replace `/PATH/TO/ENV/W/NAME` with the path where you installed `Dials` and other dependencies:

       conda activate /PATH/TO/ENV/W/NAME


Finally clone the DUI2 source code from GitHub repository:

       git clone -b v2026.1.12  https://github.com/ccp4/DUI2.git

The same tools as if installed with `curl` and `CCP4` are available, just different ways to invoke them. Remember that if you are running Dui2 from another directory, to put the full path of the `.py` file:

1. Fully local App (running both, server and client locally):

       python DUI2/src/run_dui2.py

2. Server App (Which actually runs Dials commands)

       python DUI2/src/run_dui2_server.py host=MY_HOST port=MY_PORT init_path=/PATH/TO/USER/DATA

3. Client App (GUI front end that talks to the server app)

       python DUI2/src/run_dui2_client.py url=http://...[URL of the server]

## Option 3 (EXPERIMENTAL), Installation of latest Dials and PySide6 with curl and git

This assumes you have installed `curl`, `pip` and `git` on your GNU/Linux system.

First download installer script:

       curl -L -O https://raw.githubusercontent.com/ccp4/DUI2/master/dui_instaler_w_dials_v3p25.sh

Next run the downloaded script with `bash` remember to replace `INSTALATION/DIR` with the path where you want to install all the packages:

       bash dui_instaler_w_dials_v3p25.sh INSTALATION/DIR

As in option 2 now you have available the same tools, the only difference is that now you should use `dials.python`  as your python interpreter. To launch the fully local app you should type something like:

       dials.python INSTALATION/DIR/DUI2/src/run_dui2.py

But again replace `INSTALATION/DIR` with the previously typed path. Using shell tab completion come pretty handy here, good luck.
