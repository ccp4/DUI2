# DUI2
client/server implementation of DUI (Dials User Interface)

## Installation

There are three available command line tools in the final product:

1. Server App (Which actually runs Dials commands)

TBD

2. Client App (GUI front end)

TBD

3. Fully local App (running both, server and client locally)

    This assumes you have already installed DIALS and have a BASH shell active with the DIALS environment sourced (. dials_env.sh).

    First install `pyside2`:

          libtbx.conda install -c conda-forge pyside2

    Clone the DUI2 repository (pre-release branch):

           git clone -b V0.9 https://github.com/ccp4/DUI2.git

    Run the DUI2 launcher script

          dials.python DUI2/src/all_local.py


## Requirements

This project relies on an installation of Python3 with Dials, PySide2 and Requests among other dependencies

