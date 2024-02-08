#!/bin/bash

setup_venv()
{
    if [ ! -d ."env" ]
    then
        echo "Creating Python virtual environment..."
        python3 -m venv ./.env || (echo "Failed to create venv" && exit 1)
    fi
    source .env/bin/activate
}

setup_requirements()
{
    echo "Installing requirements..."
    pip3 install -r requirements.txt || (echo "Failed to install requirements" && exit 1)
}

setup_dev()
{   
    echo "Creating development.env..."
    touch ./development.env

    echo "Installing development requirements..."
    pip3 install -r requirements_dev.txt || (echo "Failed to install development requirements" && exit 1)
}

setup_venv && echo "Virtual environment is set up."

if [[ $* == *--dev* ]]
then
    setup_dev && echo "Development requirements installed."
else
    setup_requirements && echo "Requirements installed."
fi

echo " "
echo "Activate virtual environment by running:"
echo " "
echo "  source .env/bin/activate"
echo " "
echo "Note that if you are using VS Code, it should automatically activate the environment."
echo " "
