# Set variables
HOST=0.0.0.0
PORT=8000

# Start server
echo "Starting server..."

# Dev mode

if [ "$1" == "dev" ]; then
    echo "Running in development mode"
    python -m uvicorn app.main:app --host $HOST --port $PORT --reload
elif [ "$1" == "test" ]; then
    echo "Running tests"
    python -m pytest app/tests/
else
    echo "Running in production mode"
    python -m uvicorn app.main:app --host $HOST --port $PORT
fi