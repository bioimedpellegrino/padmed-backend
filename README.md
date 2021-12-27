## PADMED ##
sudo apt-update
sudo apt-get install build-essential git # Compiler and Git
sudo apt-get install python3.8-dev python3.8-venv # or 3.7
sudo apt install python3-pip
sudo apt install python3.8-venv
sudo apt install python3-virtualenv
sudo apt-get install mysql-server
sudo apt-get install libmysqlclient-dev
sudo apt-get install python3-mediainfodll # for pymediainfo
sudo apt-get install libopenblas-dev liblapack-dev # for Dlib

# Installation of dfx #

python3 -m venv venv
source venv/bin/activate # on Windows: venv\Scripts\activate
python -m pip install --upgrade pip setuptools
python -m pip install --upgrade wheel cmake

pip install dfxapi/lib/libdfx-4.9.3.0-py3-none-linux_x86_64.whl


# ENV

# GENERAL SETTINGS
DEBUG=True
#SECRET_KEY=S3cr3t_K#Key
#SERVER=boilerplate-code-django-dashboard.appseed.us

# DFX SETTINGS
LICENCE_KEY=1209f55c-f4df-4ae1-96de-f5fe70b891b9
ORG_KEY=demo

