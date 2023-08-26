#!/bin/sh
echo "================================================================"
echo "Welcome to the setup. This will setup local virual env"
echo "----------------------------------------------------------------"

if [ -d ".env" ];
then
	echo ".env folder exists. Installing using poetry"
else
	echo "creating .env and installing poetry"
	python3 -m venv .env
fi

# Activate virual env
. .env/bin/activate

# Upgrade the PIP
pip install --upgrade pip
pip install -r requirements.txt
# Work done. so deactivate the virtual env
deactivate
