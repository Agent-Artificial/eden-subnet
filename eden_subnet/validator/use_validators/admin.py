"""This is an example of how you can write a script to launch Validators. Inherit the Validator class into a new Validator and instantiate an instance of that class when you call the script modified by the minter settings to your specificiation. Make sure the file this code is in is the first part of the Validator name. In this example it is eden which is the start of eden. Validator where Validator is the class name."""

from eden_subnet.validator.validator import Validator, ValidatorSettings
import argparse
from loguru import logger
import asyncio
import time


def parseargs():
    """
    Parse command line arguments using argparse module.

    Returns:
        argparse.Namespace: Object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--key_name", type=str, default="validator.Validator")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=10000)
    return parser.parse_args()


args = parseargs()

# Apply settings

validator_settings = ValidatorSettings(
    key_name=args.key_name,
    module_path=args.key_name,
    host=args.host,
    port=args.port,
)


# Create a new class names to let the validators have unique names.
class Validator_0(Validator):
    @logger.catch()
    def __init__(self, settings: ValidatorSettings) -> None:
        """
        Initializes the Validator class with the provided settings.

        Args:
            settings (ValidatorSettings): An instance of ValidatorSettings containing key_name, module_path, host, port, and settings.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            settings=settings,
        )


class Miner_2(Validator):
    @logger.catch()
    def __init__(self, settings: ValidatorSettings) -> None:
        """
        Initializes the Validator class with the provided settings.

        Args:
            settings (ValidatorSettings): An instance of ValidatorSettings containing key_name, module_path, host, port, and settings.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            settings=settings,
        )


class Validator_2(Validator):
    @logger.catch()
    def __init__(self, settings: ValidatorSettings) -> None:
        """
        Initializes the Validator class with the provided settings.

        Args:
            settings (ValidatorSettings): An instance of ValidatorSettings containing key_name, module_path, host, port, and settings.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            settings=settings,
        )


class Validator_3(Validator):
    @logger.catch()
    def __init__(self, settings: ValidatorSettings) -> None:
        """
        Initializes the Validator class with the provided settings.

        Args:
            settings (ValidatorSettings): An instance of ValidatorSettings containing key_name, module_path, host, port, and settings.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            settings=settings,
        )


class Validator_4(Validator):
    @logger.catch()
    def __init__(self, settings: ValidatorSettings) -> None:
        """
        Initializes the Validator class with the provided settings.

        Args:
            settings (ValidatorSettings): An instance of ValidatorSettings containing key_name, module_path, host, port, and settings.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
            settings=settings,
        )


validator_map = {
    args.key_name: Validator_0,
    args.key_name: Miner_2,
    args.key_name: Validator_2,
    args.key_name: Validator_3,
    args.key_name: Validator_4,
}

# Stager the validators for multiple instances
# i = 0
# while i < validator_settings.port - 10000:
#    i += 1
#    logger.info(f"\nStaging Validator {i}")
#    time.sleep(1)

# Serve the validator
logger.info("\nLaunching validator_settings.key_name")
validator = validator_map[validator_settings.key_name](
    settings=validator_settings,
)
validator.run_voteloop()
