#!/bin/bash

echo "Running autoflake..."
poetry run autoflake --remove-all-unused-imports --remove-unused-variable --in-place --recursive .
if [ $? -ne 0 ]; then
    echo "Autoflake failed!"
    exit 1
fi

echo "Running isort..."
poetry run isort .
if [ $? -ne 0 ]; then
    echo "isort failed!"
    exit 1
fi

echo "Running black..."
poetry run black .
if [ $? -ne 0 ]; then
    echo "Black failed!"
    exit 1
fi

echo "Linting complete!"
