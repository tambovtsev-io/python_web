#!/bin/bash

# Start the ASGI server in the background
echo "Starting the ASGI server..."
poetry run uvicorn simple_math_asgi:SimpleMathASGIServer --host 127.0.0.1 --port 8000 &

# Wait a bit to ensure the server is running
sleep 4

# Run pytest for the test.py file
echo "Running tests..."
poetry run pytest test_hw01.py

# After the tests finish, kill the server
echo "Stopping the ASGI server..."
pkill -9 uvicorn

# Exit the script
exit 0
