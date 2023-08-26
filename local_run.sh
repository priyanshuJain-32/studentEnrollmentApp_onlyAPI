#!/bin/sh
echo "============================================================"
echo "Welcome to the setup. This will setup the virual env."
echo "------------------------------------------------------------"

if [ -d ".env"];
then
	echo "Enabling virtual env"
else
	echo "No Virual env. Please run setup.sh first"
	exit N
fi

# Activate virtual env
. .env/bin/activate
export ENV=development
python app.py
deactivate
