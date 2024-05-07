import re
import types
from re import Match
from pydantic import BaseModel
from typing import List, Optional
from communex.compat.key import Ss58Address, local_key_addresses

SUBNET_NETUID = 10

IP_REGEX = re.compile(pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+")


class Module(BaseModel):
    """Module base class."""

    key_name: str
    module_path: str
    host: str
    port: int
    ss58_address: Ss58Address
    use_testnet: bool
    call_timeout: int = 60


ModuleType = types.ModuleType


class ModuleSettings(BaseModel):
    """Model for module settings."""

    module_path: str
    key_name: str
    host: str
    port: int
    ss58_address: Ss58Address
    use_testnet: bool
    IP_REGEX: re.Pattern[str] = re.compile(
        pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
    )

    class Config:
        arbitrary_types_allowed = True
        env_prefix: str = "EDEN"
        env_file: str = ".env"
        extra: str = "ignore"

    def get_ss58_address(self, key_name: str) -> Ss58Address:
        """
        Retrieves the SS58 address associated with the given key name.

        Parameters:
            key_name (str): The name of the key.

        Returns:
            str: The SS58 address corresponding to the key name.

        Raises:
            ValueError: If the key_name parameter is not provided.
        """
        local_keys = local_key_addresses()
        if not key_name:
            raise ValueError("No key_name provided")
        return local_keys[key_name]


class AccessControl(BaseModel):
    """Whitelist and blacklist model for future use."""

    whitelist: List[str] = []
    blacklist: List[str] = []


class SampleInput(BaseModel):
    """Model for sample input."""

    prompt: str
