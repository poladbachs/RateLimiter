import click
from app.main import main

@click.command()
@click.option("--demo", is_flag=True, help="Run a rate limiter demo.")
def cli(demo):
    if demo:
        import asyncio
        asyncio.run(main())

if __name__ == "__main__":
    cli()
