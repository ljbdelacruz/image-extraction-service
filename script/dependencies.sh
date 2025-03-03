#!/bin/bash

PYTHON_PATH=$(which python3)

# make copyof env file
cp .env.example .env

# install dependencies
PYTHON_PATH -m pip install --no-cache-dir -r requirements.txt

# migrate database
docker-compose up -d
prisma migrate dev
