import asyncio
import typer
import shutil
import json
from eden_subnet.validator.validator import Validator, ValidatorSettings
from eden_subnet.miner.miner import Miner, MinerSettings
from typing import Annotated
from dotenv import load_dotenv
from pathlib import Path
from importlib import import_module


load_dotenv()
app = typer.Typer()


serve_help = """
Commands:
    eden-validator:
        Serves the validator moduel.ClassNames
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
):
    """
    Serves a validator module.

    Args:
        key_name (str): The name of the key that will stake the validator. Should be in the format of <file_name>.<class_name>. Example: "validator.Validator"
        host (str): The listening ports of the validator. Defaults to "0.0.0.0".
        port (int): The open port on the system running the validator. Defaults to 50050.

    Returns:
        None
    """
    settings = ValidatorSettings(
        key_name=key_name,
        module_path=key_name,
        host=host,
        port=port,
    )
    name = key_name.split(".")[0]
    class_name = key_name.split(".")[1]
    edenpath = Path("eden_subnet/validator/eden.py")
    validatorpath = Path(f"eden_subnet/validator/{name}.py")
    if not validatorpath.exists():
        shutil.copy(edenpath, validatorpath)
        validator_text_data = json.loads(validatorpath.read_text("utf-8"))
        validator_text_data.replace("Validator_0", class_name)
    valdiator = import_module(
        name=key_name, package="eden_subnet.validator"
    ).class_name(settings)
    valdiator.validate_loop()


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
):
    """
    Serves a miner module.

    Args:
        key_name (str): The name of the key that will stake the miner. Should be in the format of <file_name>.<class_name>.
            Example: "validator.Validator"
        host (str): The listening ports of the miner. Defaults to "0.0.0.0".
        port (int): The open port on the system running the miner. Defaults to 50050.
        ss58_address (str): The SS58 address of the miner.
        use_testnet (bool, optional): Whether to use the testnet. Defaults to False.
        call_timeout (int, optional): The timeout for calls. Defaults to 60.

    Returns:
        None
    """
    settings = MinerSettings(
        key_name=key_name,
        module_path=key_name,
        host=host,
        port=port,
    )

    miner = Miner(**settings.model_dump())
    miner.serve(settings)
