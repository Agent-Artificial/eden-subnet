from eden_subnet.validator.validator import Validator, ValidatorSettings
import argparse

import time


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key_name", type=str, default="")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=10000)
    parser.add_argument("--use_testnet", type=bool, default=False)
    return parser.parse_args()


args = parseargs()

MinerSettings = ValidatorSettings(
    key_name=args.key_name,
    module_path=args.key_name,
    host=args.host,
    port=args.port,
)


class Validator_0(Validator):
    def __init__(self, settings: ValidatorSettings) -> None:
        super().__init__(settings=settings)


class Validator_1(Validator):
    def __init__(self, settings: ValidatorSettings) -> None:
        super().__init__(settings)


class Validator_2(Validator):
    def __init__(self, settings: ValidatorSettings) -> None:
        super().__init__(settings)


validator_map = {
    "eden.Validator_0": Validator_0,
    "eden.Validator_1": Validator_1,
    "eden.Validator_2": Validator_2,
}


time.sleep(0 + 10 * int(args.key_name[-1:]))

validator = validator_map[args.key_name](MinerSettings)
