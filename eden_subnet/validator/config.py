from eden_subnet.base.base import ModuleSettings

class ValidatorSettings(ModuleSettings):
    def __init__(
        self,
        key_name: str = "validator.Validator",
        module_path: str = "validator.Validator",
        host: str = "0.0.0.0",
        port: int = 50050,
        use_testnet: bool = False,
    ) -> None:
        super().__init__(
            key_name=key_name,
            module_path=module_path,
            host=host,
            port=port,
            ss58_address=self.get_ss58_address(key_name=key_name),
            use_testnet=use_testnet,