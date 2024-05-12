from eden_subnet.validator.validator import Validator, ValidatorSettings
import asyncio

Validator_1 = Validator(
    settings=ValidatorSettings(
        key_name="eden.Validator_1",
        module_path="eden.Validator_1",
        host="0.0.0.0",
        port=10000,
        use_testnet=False,
    )
)
Validator_2 = Validator(
    settings=ValidatorSettings(
        key_name="eden.Validator_2",
        module_path="eden.Validator_2",
        host="0.0.0.0",
        port=10010,
        use_testnet=False,
    )
)

asyncio.run(Validator_2.validation_loop())
