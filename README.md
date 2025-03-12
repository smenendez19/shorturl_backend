# ShortURL FastAPI Backend Project

## Description

This is a personal project of a ShortURL Backend API built with FastAPI for learning purposes.
The project has the following features:

- Routes using FastAPI.
- Schemas using Pydantic and SQLModel.
- Tests with pytest.
- Config and logging.
- SQLite database and dump data.
- Precommit hooks with black, flake8 and isort.
- Github Action to run precommit when pull request.
- Documentation in Redoc and Swagger.
- Dockerfile to create a container with the app.

## Installation and usage

The app needs Python 3.12 to run.

1. Clone the repository
2. Install the Python libraries in a virtual environment or in your global environment as you like.

    ```bash
    pip install -r requirements.txt
    ```

3. Run the app with the following command:

    ```bash
    ./start.sh
    ```

4. Run the following command if you want to run when you modify things.

    ```bash
    ./start.sh dev
    ```

5. Run the following command if you want to run the tests.

    ```bash
    ./start.sh test
    ```

6. Or, create a Docker container with Docker and run into it:

    ```bash
    docker-compose up -d
    ```

## Endpoints

- GET 'v1/docs' and '/redoc' for the documentation.
- POST 'v1/shorturl/build' to create a shorturl.
- GET 'v1/shorturl/all' to get all shorturls built.
- GET 'v1/{shorturl}' to redirect to the original url.
- GET 'v1/shorturl/{shorturl}' to get details of the shorturl.
- DELETE 'v1/shorturl/{shorturl}' to delete the shorturl.
- PUT 'v1/shorturl/{shorturl}' to update the shorturl.
- PATCH 'v1/shorturl/{shorturl}' to update the expire date of the shorturl.
