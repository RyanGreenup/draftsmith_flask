import typer


def main(port: int = 8080, public: bool = False):
    print(f"Serving on port {port}, public: {public}")


if __name__ == "__main__":
    typer.run(main)

