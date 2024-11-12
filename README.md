# Draftsmith Flask

## Configuration

The application can be configured using environment variables:

- `DRAFTSMITH_API_SCHEME`: The scheme for the API (default: "http")
- `DRAFTSMITH_API_HOST`: The hostname for the API (default: "vidar")
- `DRAFTSMITH_API_PORT`: The port for the API (default: 37240)

These can also be set via command line arguments when running the server:

```bash
python -m draftsmith_flask.main run-server --api-host=localhost --api-port=37238
```
