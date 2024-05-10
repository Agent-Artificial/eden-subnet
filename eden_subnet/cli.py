import asyncio
import typer
from eden_subnet.validator.validator import Validator
from eden_subnet.miner.miner import Miner
from eden_subnet.validator.config import ValidatorSettings
from eden_subnet.miner.config import MinerSettings
from loguru import logger
from typing import Annotated
from dotenv import load_dotenv


load_dotenv()
app = typer.Typer()


serve_help = """
Commands:
    eden-validator:
        Serves the validator module. 
        Args: 
            key_name: Name of your key that will stake the validator. Should be in the  
                format of <file_name>.<class_name>. 
                example - validator.Validator
            host: Listening ports of the validator, should be 0.0.0.0 for most users.
            port: Open port on the system you are running the validator.

"""


@app.command("serve-validator")
def serve_validator(
    key_name: Annotated[
        str,
        typer.Argument(
            help=serve_help,
        ),
    ] = "validator.Validator",
    host: Annotated[str, typer.Argument(help=serve_help)] = "0.0.0.0",
    port: Annotated[int, typer.Argument(help=serve_help)] = 50050,
    use_testnet: Annotated[bool, typer.Option] = True,
):
    settings = ValidatorSettings(
        key_name=key_name,
        module_path=key_name,
        host=host,
        port=port,
        use_testnet=use_testnet,
    )
    validator = Validator(settings)
    asyncio.run(validator.serve())


@app.command("serve-miner")
def serve_miner(
    key_name: Annotated[
        str,
        typer.Argument(
            help=serve_help,
        ),
    ] = "miner.Miner",
    host: Annotated[str, typer.Argument(help=serve_help)] = "0.0.0.0",
    port: Annotated[int, typer.Argument(help=serve_help)] = 50051,
    use_testnet: Annotated[bool, typer.Option] = True,
):
    settings = MinerSettings(
        key_name=key_name,
        module_path=key_name,
        host=host,
        port=port,
        use_testnet=use_testnet,
    )
    miner = Miner(settings)
    asyncio.run(miner.serve())
