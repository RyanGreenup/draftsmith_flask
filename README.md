# Draftsmith Flask

## Usage

Due to limitations with with Python server's, the API information cannot be passed as arguments and must be inherited from the environment. For this reason,
the server must be run with the following command:

- Development
    ```bash
    API_SCHEME=http API_PORT=37240 API_HOST=vidar poetry run python server.py
    ```
- Production
    ```bash
    API_SCHEME=http API_PORT=37240 API_HOST=vidar gunicorn -w 4 -b 0.0.0.0:5000 server:app
    ```

My hostname is `vidar`, in the docker container it will (likely) be `app`, adjust accordingly.
