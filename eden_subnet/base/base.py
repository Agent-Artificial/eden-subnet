import re

import requests
from importlib import import_module
from re import Match
from pydantic import BaseModel
from communex.compat.key import Ss58Address
from typing import List, Optional, Tuple, Dict
from loguru import logger
from communex.client import CommuneClient
from communex._common import get_node_url
from eden_subnet.base.data_models import (
    ModuleSettings,
    Module,
    SUBNET_NETUID,
)

IP_REGEX = re.compile(pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+")
c_client: CommuneClient = CommuneClient(url=get_node_url(use_testnet=False))


class Message(BaseModel):
    """
    A class representing a message.

    Explanation:
    This class defines a data model for a message with attributes 'content' of type str and 'role' of type str.
    """

    content: str
    role: str


class BaseModule(Module):
    """
    A class representing a base module.

    Explanation:
    This class extends Module and includes attributes related to module settings, miner lists, keys, and network addresses. It provides methods for dynamic import, extracting addresses from strings, retrieving netuids, and getting IP ports from module addresses.
    """

    settings: ModuleSettings
    miner_list: List[Tuple[str, Ss58Address]]
    checked_list: List[Tuple[str, Ss58Address]]
    saved_key: Optional[Dict[str, str]]
    checking_list: List[Tuple[str, Ss58Address]]
    netuid: int = SUBNET_NETUID

    class Config:
        """
        A configuration class.

        Explanation:
        This class defines configuration settings with 'arbitrary_types_allowed' set to True and 'extra' set to 'ignore'.
        """

        arbitrary_types_allowed = True
        extra = "ignore"

    def __init__(
        self,
        settings: ModuleSettings,
        key_name: str,
        module_path: str,
        host: str,
        port: str,
    ) -> None:
        """
        Initializes the class with the provided settings and parameters.

        Parameters:
            settings (ModuleSettings): The settings object containing module settings.
            key_name (str): The name of the key.
            module_path (str): The path of the module.
            host (str): The host value.
            port (str): The port value.

        Returns:
            None
        """
        super().__init__(
            key_name=settings.key_name or key_name,
            module_path=settings.module_path or module_path,
            host=settings.host or host,
            port=settings.port or int(port),
        )

    def dynamic_import(self) -> Module:
        """
        Imports and dynamically retrieves a module based on the provided module path.

        Returns:
            Module: The imported module.
        """
        module_name, class_name = self.module_path.rsplit(sep=".", maxsplit=1)
        try:
            module: Module = import_module(name=f"eden_subnet.miner.{module_name}")  # type: ignore
        except ImportError as e:
            logger.error(f"Module not found: {e}")
        return getattr(module, class_name)

    @staticmethod
    def extract_address(string: str) -> re.Match[str] | None:
        """
        Extracts an address from a given string.

        Parameters:
            string (str): The string from which to extract the address.

        Returns:
            re.Match[str] | None: A match object containing the extracted address if found,
            otherwise None.
        """
        try:
            return re.search(pattern=IP_REGEX, string=string)
        except Exception as e:
            logger.error(f"Error extracting address: {e}")
        return None

    @staticmethod
    def get_netuid(client: CommuneClient, subnet_name: str = "Eden") -> int:
        """
        Retrieves the netuid associated with a given subnet name from the provided CommuneClient.

        Parameters:
            client (CommuneClient): The commune client object.
            subnet_name (str, optional): The name of the subnet to retrieve the netuid for. Defaults to "Eden".

        Returns:
            int: The netuid associated with the provided subnet name.

        Raises:
            ValueError: If the subnet name is not found in the subnets queried from the client.
        """
        subnets: dict[int, str] = client.query_map_subnet_names()
        for netuid, name in subnets.items():
            if name == subnet_name:
                logger.info("use netuid:", netuid)
                return netuid
        raise ValueError(f"Subnet {subnet_name} not found")

    @staticmethod
    def get_ip_port(modules_addresses: Dict[int, str]) -> Dict[int, List[str]]:
        """
        Retrieves IP addresses and ports from a dictionary of module addresses.

        Parameters:
            modules_addresses (Dict[int, str]): A dictionary mapping module IDs to their addresses.

        Returns:
            Dict[int, List[str]]: A dictionary mapping module IDs to a list of IP addresses and ports.
        """
        filtered_addr: dict[int, Match[str] | None] = {
            id: BaseValidator.extract_address(string=addr)
            for id, addr in modules_addresses.items()
        }
        ip_port: dict[int, list[str]] = {
            id: x.group(0).split(":")
            for id, x in filtered_addr.items()
            if x is not None
        }
        return ip_port


class BaseValidator(BaseModule):
    """
    A class representing a base validator.

    Explanation:
    This class extends BaseModule and includes attributes related to validator settings and operations. It provides methods for making validation requests, getting miner generations, querying miners, scoring miners, and validating input.
    """

    key_name: str
    module_path: str
    host: str
    port: int
    settings: ModuleSettings
    __pydantic_fields_set__ = {
        "key_name",
        "module_path",
        "host",
        "port",
        "settings",
    }

    def __init__(
        self,
        config: ModuleSettings,
        key_name: str,
        module_path: str,
        host: str,
        port: str,
    ) -> None:
        """
        Initializes the class with the provided settings and parameters.

        Parameters:
            config (ModuleSettings): The settings object containing module settings.
            key_name (str): The name of the key.
            module_path (str): The path of the module.
            host (str): The host value.
            port (str): The port value.

        Returns:
            None
        """
        super().__init__(
            settings=config,
            key_name=config.key_name or key_name,
            module_path=config.module_path or module_path,
            host=config.host or host,
            port=str(config.port) or port,
        )
        self.settings = config

    def make_validation_request(self, uid, miner_input, module_host, module_port):
        """
        Sends a validation request to the specified module and returns the result.

        Args:
            uid (str): The unique identifier for the validation request.
            miner_input (Message): The input message for the validation request.
            module_host (str): The host of the module to send the request to.
            module_port (int): The port of the module to send the request to.

        Returns:
            dict: A dictionary containing the unique identifier as the key and the result of the validation request as the value.

        Raises:
            ValueError: If an error occurs during the validation request.

        """
        try:
            url = f"http://{module_host}:{module_port}/generate"
            reponse = requests.post(url, json=miner_input.model_dump(), timeout=30)
            if reponse.status_code == 200:
                result = reponse.content
                return {uid: result}
        except ValueError as e:
            logger.error(e)
        return {uid: b"0x00001"}

    def get_miner_generation(
        self,
        miner_list: tuple[list[str], dict[str, int]],
        miner_input: Message,
    ):
        """
        Retrieves the generation of miners based on the provided miner list and input message.

        Args:
            miner_list (tuple[list[str], dict[str, int]]): A tuple containing a list of miner names and a dictionary mapping miner names to their corresponding netuids.
            miner_input (Message): The input message for the validation request.

        Returns:
            dict: A dictionary containing the netuids as keys and the results of the validation requests as values.

        Raises:
            ValueError: If an error occurs during the validation request.
        """
        results_dict = {}
        for miner_dict in miner_list:
            uid: str = miner_dict["netuid"]  # type: ignore
            keys = c_client.query_map_key(netuid=10)
            miner_ss58_address = keys["netuid"]
            module_host, module_port = miner_dict["address"]
            logger.debug(
                f"\nUid: {uid}\nAddress: {miner_ss58_address}\nModule host:{module_host}\nModule port: {module_port}"
            )
            result = self.make_validation_request(
                uid=uid,
                miner_input=miner_input,
                module_host=module_host,
                module_port=module_port,
            )
            results_dict[uid] = result
        return results_dict

    def get_queryable_miners(self) -> dict[int, tuple[str, int]] | None:
        """
        Retrieves queryable miners and their corresponding information.

        Returns:
            dict[int, tuple[str, int]] | None: A dictionary with netuids as keys and tuple of address and port as values, or None if an error occurs.

        Raises:
            RuntimeError: If an error occurs during the retrieval process.
        """
        try:
            module_addresses = c_client.query_map_address(netuid=SUBNET_NETUID)
            module_keys = c_client.query_map_key(netuid=SUBNET_NETUID)
            if module_addresses:
                module_addresses = dict(module_addresses.items())
            if module_keys:
                modules_keys = dict(module_keys.items())
            module_dict = {}
            modules_filtered_address = BaseValidator.get_ip_port(
                modules_addresses=module_addresses
            )
            for module_id, ss58_address in modules_keys.items():
                module_info = {}
                if module_id == 0:  # skip master
                    continue
                if ss58_address == self.settings.get_ss58_address(
                    key_name=self.key_name
                ):  # skip yourself
                    continue
                if ss58_addr := modules_filtered_address.get(module_id):
                    module_info["netuid"] = module_id
                    module_info["address"] = ss58_addr
                module_host_address = module_addresses[module_id]
                if module_host_address := modules_filtered_address.get(module_id):
                    if ":" in module_host_address:
                        host, port = module_host_address[module_id].split(":")
                        module_info["host"] = host
                        module_info["port"] = port
                module_dict[module_id] = module_info
            return module_dict
        except RuntimeError as e:
            logger.error(e)

    def score_miner(self, module_info):
        """
        Calculates the score for a miner based on their module information.

        Args:
            module_info (dict): A dictionary containing the module information of the miner.
                It should have the following keys:
                - "netuid" (int): The netuid of the miner.
                - "ss58_address" (str): The ss58 address of the miner.

        Returns:
            dict: A dictionary containing the module information of the miner, including the weight.
                The dictionary has the following structure:
                - "netuid" (int): The netuid of the miner.
                - "weight" (float): The weight of the miner.

        Raises:
            RuntimeError: If the ss58_address of the miner is not registered in the subnet.
        """
        netuid = module_info["netuid"]
        weights_dict = c_client.query_map_weights(netuid=netuid)
        ss58_key = module_info["ss58_address"]
        if ss58_key not in weights_dict:
            raise RuntimeError(f"validator key {ss58_key} is not registered in subnet")
        modules_info = {}
        weights = weights_dict[ss58_key]
        if netuid in modules_info:
            modules_info[netuid]["weight"] += weights
        else:
            modules_info[netuid] = {"weight": weights}
        return modules_info

    def validate_input(self, miner_response, sample_embedding):
        raise NotImplementedError
