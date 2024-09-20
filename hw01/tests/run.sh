#!/bin/bash

# Get the absolute path to the directory containing the script
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$TESTS_DIR/.."  # This assumes simple_math_asgi is one level above tests

# Set the PYTHONPATH to include the project directory
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Start the ASGI server in the background
echo "Starting the ASGI server..."
poetry run python "$PROJECT_DIR/simple_math_asgi.py" & server_pid=$!

# Wait a bit to ensure the server is running
sleep 4

# Run pytest for the test.py file
echo "Running tests..."
poetry run pytest "$TESTS_DIR/test_hw01.py"

# After the tests finish, kill the server
echo "Stopping the ASGI server..."
kill -9 $server_pid
pkill -9 python

# Exit the script
exit 0
