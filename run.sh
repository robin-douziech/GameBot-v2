#!/bin/bash

if [ "$#" -ge 1 ] && [ "$1" = "-r" ]
then

	if [ -d venv ]
	then
		echo "Removing virtual environment"
		rm -r venv
	fi

	echo "Creating new virtual environment"
	python3 -m venv venv

	echo "Activating virtual environment"
	source venv/bin/activate

	echo "Installing dependencies"
	pip install -r requirements.txt

else

	echo "Activating virtual environment"
	source venv/bin/activate

fi

echo "Running GameBot"
nohup python3 src/run.py &