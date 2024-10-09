# Dockerising this app

## Dev vs Prod
Separation into `development` and `production` stages:

1. Development Stage:
  - Mounts the app directory, allowing for live code changes without rebuilding the image.
  - Uses `uvicorn` auto-reload

2. Production Stage:
  - Copies the application code into the image instead of mounting it.

### Usage

#### Building
1. For Development:
  - Build the image up to the development stage:
    ```
    docker build --target development -t shop_api-server:dev .
    ```
  - Run the container, mounting your local code directory:
    ```
    docker run -v $(pwd)/app:/app -p 8000:8000 shop_api-server:dev
    ```

2. For Production:
  - Build the complete image:
    ```
    docker build -t shop_api-server:prod .
    ```
  - Run the container:
    ```
    docker run -p 8000:8000 shop_api-server:prod
    ```

#### Running
- For development:
  ```
  docker-compose --profile dev up
  ```
  Access the app at http://localhost:8000

- For production:
  ```
  docker-compose --profile prod up
  ```
  Access the app at http://localhost:8001

- To run specific container:
  ```
  docker-compose up <container>
  ```
