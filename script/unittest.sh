#!/bin/bash

# assign python path
PYTHON_PATH=$(which python3)

# run unit test service
$PYTHON_PATH -m unittest discover -s tests/service -p "test_*.py"