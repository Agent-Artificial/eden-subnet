import asyncio
import base64
import re

import requests
from importlib import import_module
from re import Match
from pydantic import Field, BaseModel
from typing import List, Optional, Tuple, Dict
from loguru import logger
from communex.client import CommuneClient
from communex._common import get_node_url
from communex.types import Ss58Address
from eden_subnet.base.config import (
    ModuleSettings,
    Module,
    SUBNET_NETUID,
)

IP_REGEX = re.compile(pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+")
c_client: CommuneClient = CommuneClient(url=get_node_url(use_testnet=False))


class Message(BaseModel):
    content: str
    role: str


class BaseModule(Module):
    """Base validator class to inherit."""

    settings: ModuleSettings

    netuid: int = SUBNET_NETUID

    class Config:
        arbitrary_types_allowed = True
        extra = "ignore"

    def __init__(
        self,
        key_name: str,
        module_path: str,
        host: str,
        port: int,
        ss58_address: str,
        use_testnet: bool,
        call_timeout: int = 60,
    ) -> None:
        settings = {
            "key_name": key_name,
            "module_path": module_path,
            "host": host,
            "port": port,
            "ss58_address": ss58_address,
            "use_testnet": use_testnet,
            "call_timeout": call_timeout,
        }

    def dynamic_import(self) -> Module:
        module_name, class_name = self.settings.module_path.rsplit(sep=".", maxsplit=1)
        try:
            module: Module = import_module(name=f"eden_subnet.miner.{module_name}")  # type: ignore
        except ImportError as e:
            logger.error(f"Module not found: {e}")
        return getattr(module, class_name)

    @staticmethod
    def extract_address(string: str) -> re.Match[str] | None:
        return re.search(pattern=IP_REGEX, string=string)

    @staticmethod
    def get_netuid(client: CommuneClient, subnet_name: str = "Eden") -> int:
        subnets: dict[int, str] = client.query_map_subnet_names()
        for netuid, name in subnets.items():
            if name == subnet_name:
                logger.info("use netuid:", netuid)
                return netuid
        raise ValueError(f"Subnet {subnet_name} not found")

    @staticmethod
    def get_ip_port(modules_addresses: Dict[int, str]) -> Dict[int, List[str]]:
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
    key_name: str = Field(default="")
    module_path: str = Field(default="")
    host: str = Field(default="")
    port: int = Field(default=0)
    ss58_address: str = Field(default="")
    use_testnet: bool = Field(default=False)
    call_timeout: int = Field(default=60)

    def __init__(self, config: ModuleSettings) -> None:
        super().__init__(**config.model_dump())
        self.settings = config

    def make_validation_request(self, uid, miner_input, module_host, module_port):
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
                if ss58_address == self.settings.ss58_address:  # skip yourself
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
