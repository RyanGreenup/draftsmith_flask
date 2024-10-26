import typer
from server import app  # Import the Flask app


def main(port: int = 8080, host: str = "0.0.0.0", debug: bool = False, api_host: str = "localhost", api_port: int = 37238):
    if host == "0.0.0.0":
        print("Warning: Server is accessible from any IP address. Use with caution.")
    print(f"Serving on {host}:{port}")
    app.run(host=host, port=port)


if __name__ == "__main__":
    typer.run(main)
