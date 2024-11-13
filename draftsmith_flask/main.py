#!/usr/bin/env python3
import os
import typer
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
import draftsmith_flask.server as srv

app = typer.Typer()

@app.command()
def run_server(
    port: int = typer.Option(8080, help="Port to run the server on"),
    host: str = typer.Option("0.0.0.0", help="Host to bind the server to"),
    debug: bool = typer.Option(False, help="Use Flask Debug Server"),
    api_scheme: str = typer.Option(
        "http",
        help="API scheme (http or https)"
    ),
    api_host: str = typer.Option(
        "localhost",
        help="API host (This is the name of the server other devices will see, e.g. 'myserver' or in docker: 'app' / 'service-name')"
    ),
    api_port: int = typer.Option(37238, help="API port"),
):
    """
    Run the Flask application server.
    """
    if host == "0.0.0.0":
        print("Warning: Server is accessible from any IP address. Use with caution.")

    # Set API host and port in Flask app configuration
    srv.app.config['API_HOST'] = api_host
    srv.app.config['API_PORT'] = api_port
    srv.app.config['API_SCHEME'] = api_scheme

    config = Config()
    config.bind = [f"{host}:{port}"]
    config.debug = debug

    print(f"Serving on {host}:{port} with API host {api_host}:{api_port}")
    asyncio.run(serve(srv.app, config))

if __name__ == "__main__":
    app()

