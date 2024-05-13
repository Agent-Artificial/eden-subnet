"""This is an example of how you can write a script to launch Validators. Inherit the Validator class into a new Validator and instantiate an instance of that class when you call the script modified by the minter settings to your specificiation. Make sure the file this code is in is the first part of the Validator name. In this example it is eden which is the start of eden. Validator where Validator is the class name."""

from eden_subnet.validator.validator import Validator, ValidatorSettings
import argparse

import time


def parseargs():
    """
    Parse command line arguments using argparse module.

    Returns:
        argparse.Namespace: Object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--key_name", type=str, default="")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=10000)
    parser.add_argument("--use_testnet", type=bool, default=False)
    return parser.parse_args()


args = parseargs()

# Apply settings

ValiSettings = ValidatorSettings(
    key_name=args.key_name,
    module_path=args.key_name,
    host=args.host,
    port=args.port,
)


# Create a new class names to let the validators have unique names.
class Validator_0(Validator):
    def __init__(self, settings: ValidatorSettings) -> None:
        """
        Initializes the Validator object with the provided settings.

        Args:
            settings (ValidatorSettings): The settings object containing validator configuration.

        Returns:
            None
        """
        super().__init__(settings=settings)


class Validator_1(Validator):
    def __init__(self, settings: ValidatorSettings) -> None:
        """
        Initializes the Validator object with the provided settings.

        Args:
            settings (ValidatorSettings): The settings object containing validator configuration.

        Returns:
            None
        """
        super().__init__(settings)


class Validator_2(Validator):
    def __init__(self, settings: ValidatorSettings) -> None:
        """
        Initializes the Validator object with the provided settings.

        Args:
            settings (ValidatorSettings): The settings object containing validator configuration.

        Returns:
            None
        """
        super().__init__(settings)


validator_map = {
    "eden.Validator_0": Validator_0,
    "eden.Validator_1": Validator_1,
    "eden.Validator_2": Validator_2,
}

# Stager the validators for multiple instances
time.sleep(0 + 10 * int(args.key_name[-1:]))

# Serve the validator

validator = validator_map[args.key_name](ValidatorSettings)
