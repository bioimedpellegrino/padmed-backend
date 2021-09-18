## PADMED ##

sudo apt-get install build-essential git # Compiler and Git
sudo apt-get install python3.8-dev python3.8-venv # or 3.7
sudo apt-get install python3-mediainfodll # for pymediainfo
sudo apt-get install libopenblas-dev liblapack-dev # for Dlib

# Installation of dfx #

python3 -m venv venv
source venv/bin/activate # on Windows: venv\Scripts\activate
python -m pip install --upgrade pip setuptools
python -m pip install --upgrade wheel cmake

pip install dfxapi/lib/libdfx-4.9.3.0-py3-none-linux_x86_64.whl
