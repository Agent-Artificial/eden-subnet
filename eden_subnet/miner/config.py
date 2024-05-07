from pydantic import BaseModel
from typing import Literal
from eden_subnet.base.config import ModuleSettings


class TokenUsage(BaseModel):
    total: int
    prompt: int
    request: int
    response: int


class MinerSettings(ModuleSettings):
    """
    Settings for the Miner.
    """

    def __init__(
        self,
        key_name: str = "miner.Miner",
        module_path: str = "miner.Miner",
        host: str = "0.0.0.0",
        port: int = 50051,
        use_testnet: bool = False,
    ) -> None:
        """
        Initializes the MinerSettings class with default values for the key_name and module_path.

        Parameters:
            key_name (str, optional): The name of the key. Defaults to "".
            module_path (str, optional): The path of the module. Defaults to "".

        Returns:
            None
        """
        super().__init__(
            key_name=key_name,
            module_path=module_path,
            host=host,
            port=port,
            ss58_address=self.get_ss58_address(key_name=key_name),
            use_testnet=use_testnet,
        )


class Message(BaseModel):
    content: str
    role: Literal["user", "assistant", "system"]
