import asyncio
import typer
from eden_subnet.validator.validator import Validator
from eden_subnet.miner.miner import Miner
from eden_subnet.validator.config import ValidatorSettings
from communex.compat.key import Ss58Address
from typing import Annotated
from dotenv import load_dotenv
import importlib


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
    asyncio.run(validator.validation_loop())


@app.command("serve-miner")
def serve_miner(
    key_name: Annotated[
        str,
        typer.Argument(
            help=serve_help,
        ),
    ],
    host: Annotated[str, typer.Argument(help=serve_help)],
    port: Annotated[int, typer.Argument(help=serve_help)],
    ss58_address: Annotated[str, typer.Argument(help=serve_help)],
    use_testnet: Annotated[bool, typer.Option] = False,
    call_timeout: Annotated[int, typer.Option] = 60,
):
    miner = Miner(
        key_name=key_name,
        module_path=key_name,
        host=host,
        port=port,
        ss58_address=Ss58Address(ss58_address),
        use_testnet=use_testnet,
        call_timeout=call_timeout,
    )
    miner.serve()
