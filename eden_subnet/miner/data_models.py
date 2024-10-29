from pydantic import BaseModel, Field
from typing import Literal, Dict, List, Optional, Union
from eden_subnet.base.data_models import ModuleSettings


class TokenUsage(BaseModel):
    """Token usage model"""

    total_tokens: int = 0
    prompt_tokens: int = 0
    request_tokens: int = 0
    response_tokens: int = 0


class MinerSettings(ModuleSettings):
    """
    Settings for the Miner.
    """

    def __init__(
        self,
        key_name: str,
        module_path: str,
        host: str,
        port: int,
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
        )


class Message(BaseModel):
    content: str
    role: Literal["user", "assistant", "system"]


class EmbeddingRequest(BaseModel):
    messages: List[Union[Message, Dict[str, str]]]
    models: Optional[List[str]]
    api_key: Optional[str]