import random
import json
import time
import os
import requests
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
from typing import Any, List, Union, Tuple, Dict
from fastapi.exceptions import HTTPException
from communex.compat.key import Keypair
from communex.client import CommuneClient
from communex._common import get_node_url
from pydantic import BaseModel
from eden_subnet.base.base import Message
from eden_subnet.validator.data_models import TOPICS
from eden_subnet.miner.tiktokenizer import TikTokenizer
from eden_subnet.validator.sigmoid import sigmoid
from eden_subnet.base.data_models import SampleInput
from dotenv import load_dotenv

load_dotenv()

tokenizer = TikTokenizer()
comx = CommuneClient(get_node_url())


OMIT_ADDRESS_LIST = [
    "5FjyW3vcB8MkDh19JV88dVLGP6wQEftJC6nXUEobQmdZc6PY",
    "5Dqz1mcuBjKvXLRoPgNikSambGDCMaUPMmbsx8vkXfRAKLQU",
    "5DRehMw43SRj93wHieGV1QS2fZBwNvHpRgkmkxWotfQns5Xy",
]


class Ss58Address(BaseModel):
    """
    A class representing an SS58 address.

    Explanation:
    This class defines a data model for an SS58 address with a single attribute 'address' of type str.
    """

    address: str  # Example field, adjust as needed


class ConfigDict(BaseModel):
    """
    A class representing a configuration dictionary.

    Explanation:
    This class defines a data model for a configuration dictionary with a single attribute 'arbitrary_types_allowed' that specifies whether arbitrary types are allowed by default.
    """

    arbitrary_types_allowed: bool = True


class ValidatorSettings(BaseModel):
    """
    A class representing validator settings.

    Explanation:
    This class defines a data model for validator settings including attributes like key name, module path, host, and port. Additional settings can be added as needed.
    """

    key_name: str
    module_path: str
    host: str
    port: int


class Validator:
    key_name: str
    module_path: str
    host: str
    port: int
    settings: ValidatorSettings

    def __init__(
        self,
        key_name: str,
        module_path: str,
        host: str,
        port: int,
        settings: ValidatorSettings,
    ) -> None:
        self.key_name = key_name or settings.key_name
        self.module_path = module_path or settings.module_path
        self.host = host or settings.host
        self.port = port or settings.port
        self.settings = settings

    async def make_request(self, messages: List[Message], input_url: str = ""):
        try:
            payload = json.dumps(
                {
                    "messages": [message.model_dump() for message in messages],
                    "model": str(os.getenv("AGENTARTIFICIAL_MODEL")),
                }
            )
            headers = {
                "Content-Type": "application/json",
                "Authorization": str(os.getenv("AGENTARTIFICIAL_API_KEY")),
            }

            response = requests.request(
                method="POST",
                url=input_url,
                headers=headers,
                data=payload,
                timeout=30,
            )
            if response.status_code == 200:
                print(response.json())

                return response.json()["choices"][0]["message"]["content"]
        except HTTPException as e:
            logger.error(f"Error making request: {e}")

    def encode_response(self, response):
        return tokenizer.embedding_function.encode(response)

    async def get_sample_result(self):
        logger.info("getting sample result")
        topic = random.choice(TOPICS)
        logger.debug(f"sample topic:\n{topic}")
        topic_message = Message(
            content=f"Please write a short alegory about this topic: {topic}",
            role="user",
        )
        logger.debug(f"\nSample Topic:\n{topic_message}")
        sample_result = await self.make_request(
            messages=[topic_message], input_url=str(os.getenv("AGENTARTIFICIAL_URL"))
        )
        logger.debug(f"\nSample Result:\n{sample_result}")
        return sample_result

    def validate_input(self, embedding1, embedding2):
        logger.info("\nevaluating sample similarity")
        result = tokenizer.cosine_similarity(
            embedding1=embedding1, embedding2=embedding2
        )
        logger.debug(f"\nsimilarity result: {result.hex()[:10]}...")
        return result

    def load_local_key(self):
        keypath = (
            Path(f"$HOME/.commune/key/{self.key_name}.json").expanduser().resolve()
        )
        with open(keypath, "r", encoding="utf-8") as f:
            key = json.loads(f.read())["data"]
            private_key = json.loads(key)["private_key"]
            ss58address = json.loads(key)["ss58_address"]
            return Keypair(private_key=private_key, ss58_address=ss58address)

    async def get_similairities(self, selfuid, encoding, prompt_message, addresses):
        miner_responses = {}
        for uid, address in addresses.items():
            if uid == selfuid:
                continue
            url = f"https://{address}/generate"
            if f"https://{self.host}:{self.port}/generate" == url:
                continue
            try:
                response = await self.make_request(
                    messages=[prompt_message], input_url=url
                )
            except Exception as e:
                logger.debug(e)
                continue
            miner_responses[uid] = self.validate_input(encoding, response)
            return miner_responses

    async def validate_loop(self):
        selfuid, _ = self.get_index(self.port - 10000)

        address_dict = self.parse_addresses()

        weights_dict = self.parse_weights()
        weights_dict = self.check_weights(selfuid, weights_dict, address_dict)

        keys_dict = self.parse_keys()

        sample_result = await self.get_sample_result()
        prompt_message = Message(content=str(sample_result), role="user")
        encoding = self.encode_response(sample_result)
        similiarity_dict = await self.get_similairities(
            selfuid, encoding, prompt_message, address_dict
        )

        score_dict = self.score_modules(
            weights_dict, address_dict, keys_dict, similiarity_dict
        )

        keypair = self.load_local_key()
        uids = []
        weights = []
        for uid, weight in score_dict.items():
            if uid == selfuid:
                continue
            uids.append(uid)
            weights.append(weight)

        comx.vote(key=keypair, netuid=10, weights=weights, uids=uids)

        time.sleep(120)

    def get_index(self, index):
        index_map = {0: 51, 1: 1, 2: 5}
        keyname_map = {
            0: "eden.Validator_0.json",
            1: "eden.Validator_1.json",
            2: "eden.Validator_2.json",
        }
        keyname = keyname_map[index]
        selfuid = index_map[index]
        return selfuid, keyname

    def parse_addresses(self):
        return comx.query_map_address(netuid=10)

    def parse_weights(self):
        # sourcery skip: dict-comprehension, identity-comprehension, inline-immediately-returned-variable
        weights = comx.query_map_weights(netuid=10)[1]
        weight_dict = {}
        for uid, weight in weights:  # type: ignore
            if uid not in weight_dict:
                weight_dict[uid] = weight
        return weight_dict

    def parse_stake(self):
        return comx.query_map_stake(netuid=10)

    def check_weights(self, selfuid, weights, addresses):
        for uid, _ in addresses.items():
            if uid not in weights and uid != selfuid:
                weights[uid] = 30

        return weights

    def parse_keys(self):
        return comx.query_map_key(netuid=10)

    def scale_numbers(self, numbers):
        min_value = min(numbers)
        max_value = max(numbers)
        return [(number - min_value) / (max_value - min_value) for number in numbers]

    def list_to_dict(self, list):
        return {i: list[i] for i in range(len(list))}

    def scale_dict_values(self, dictionary):
        return {
            key: (value - min(dictionary.values()))
            / (max(dictionary.values()) - min(dictionary.values()))
            for key, value in dictionary.items()
        }

    def score_modules(self, weights_dict, staketos_dict, keys_dict, similairity_dict):
        """
        Calculates the score of modules based on weights, staketos, keys, and similarity values.

        Parameters:
            weights_dict (dict): A dictionary mapping user IDs to their weights.
            staketos_dict (dict): A dictionary mapping user IDs to their stake values.
            keys_dict (dict): A dictionary mapping unique IDs to their keys.
            similarity_dict (dict): A dictionary mapping user IDs to their similarity values.

        Returns:
            A dictionary mapping user IDs to their calculated scores.
        """
        staketos = {}
        for uid, key in keys_dict.items():
            if key in staketos_dict:
                staketo = staketos_dict[key]
                staketos[uid] = staketo
        scaled_staketos_dict = self.scale_dict_values(staketos)
        scaled_weight_dict = self.scale_dict_values(weights_dict)
        scaled_similairity_dict = self.scale_dict_values(similairity_dict)
        scaled_scores = {}
        for uid in keys_dict.keys():
            if uid in scaled_staketos_dict:
                stake = scaled_staketos_dict[uid]
            calculated_score = (
                scaled_weight_dict[uid] * 0.2
                + stake * 0.2
                + scaled_similairity_dict[uid] * 0.6
            ) / 3
            scaled_scores[uid] = calculated_score
        return self.scale_dict_values(scaled_scores)
