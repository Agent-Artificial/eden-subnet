import random
import json
import asyncio
import time
import base64
import uvicorn
import os
import requests
from requests import Request
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
from typing import Any, Literal, List, Union, Tuple, Dict
from numpy import floating
from numpy._typing import _64Bit
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from communex.compat.key import Keypair
from communex.client import CommuneClient
from communex._common import get_node_url
from pydantic import Field, BaseModel
from eden_subnet.base.base import Message
from eden_subnet.miner.data_models import Message
from eden_subnet.validator.data_models import TOPICS
from eden_subnet.miner.tiktokenizer import TikTokenizer
from eden_subnet.validator.sigmoid import threshold_sigmoid_reward_distribution
from dotenv import load_dotenv

load_dotenv()


c_client = CommuneClient(get_node_url())

tokenizer = TikTokenizer()

VALI_KEY_FILEPATH = "/home/ubuntu/.commune/key/eden.Validator_1.json"


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


class BaseValidator(BaseModel):
    """
    A class representing a base validator.

    Explanation:
    This class serves as a base model for validators and includes attributes such as key name, module path, host, and port.
    """

    key_name: str
    module_path: str
    host: str
    port: int


class Validator(BaseValidator):
    """
    A class representing a Validator.

    Explanation:
    This class extends BaseValidator and includes various attributes related to validator settings and operations. It provides methods for making requests, retrieving miners, getting keys, validating input, setting weights, running a validation loop, and serving the validator asynchronously.
    """

    key_name: str = Field(default="")
    module_path: str = Field(default="")
    host: str = Field(default="")
    port: int = Field(default=0)
    miner_list: List[Tuple[str, Ss58Address]] = Field(default_factory=list)
    checked_list: List[Tuple[str, Ss58Address]] = Field(default_factory=list)
    saved_key: Union[Dict[Any, Any], None] = Field(default=None)
    checking_list: List[Tuple[str, Ss58Address]] = Field(default_factory=list)
    ss58_address: Ss58Address = Field(default_factory=None)
    model_config: ConfigDict = Field(
        default_factory=lambda: ConfigDict(arbitrary_types_allowed=True)
    )
    settings: ValidatorSettings = Field(default_factory=None)

    def __init__(self, settings: ValidatorSettings) -> None:
        """
        Initializes the Validator object with the provided settings.

        Explanation:
        This function initializes the Validator object using the settings provided, including key name, module path, host, and port. It also retrieves and stores the saved key information and logs the initialization details.

        Args:
        - settings (ValidatorSettings): The settings object containing validator configuration.

        Returns:
        - None
        """
        super().__init__(
            key_name=settings.key_name,
            module_path=settings.module_path,
            host=settings.host,
            port=settings.port,
        )

        self.settings = settings
        self.saved_key = (
            json.loads(str(self.get_key(self.key_name))) if self.key_name else None
        )
        logger.info(f"Initializing validator with settings: {settings.model_dump()}")

    @logger.catch
    async def make_request(self, messages: List[Message], input_url: str = ""):
        """
        Makes a request using the provided messages and input URL. Returns the content of the first choice message from the response.

        Args:
        - messages (List[Message]): List of messages to be sent in the request.
        - input_url (str): The URL to send the request to. If not provided, uses the default URL from the environment variables.

        Returns:
        - str: The content of the first choice message from the response.
        """
        try:
            url = input_url or os.getenv("AGENTARTIFICIAL_URL")
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
                method="POST", url=str(url), headers=headers, data=payload, timeout=30
            )
            print(response.json())

            return response.json()["choices"][0]["message"]["content"]
        except ValueError as e:
            logger.error(f"Error making request: {e}")

    def get_miner_by_netuid(self, miner_id: int):
        """
        Retrieves the miner's ss58 address based on the provided miner ID.

        Parameters:
            miner_id (int): The ID of the miner.

        Returns:
            str: The ss58 address of the miner if found, None otherwise.
        """
        logger.info("getting miner by netuid")
        miners = self.get_queryable_miners()
        for miner, ss58 in miners:  # type: ignore
            if miner_id in miner:
                return ss58
            return

    def get_key(self, key_name: str):
        """
        Retrieves the validator key from the local storage based on the provided key name.

        Parameters:
            key_name (str): The name of the key to retrieve.

        Returns:
            str: The validator key if found, None otherwise.

        Raises:
            ValueError: If the key is not found in the local storage.
        """
        logger.info("getting validator key from local storage")
        try:
            key_dir = Path("~/.commune/key").expanduser().resolve()
            keypaths = key_dir.iterdir()
            for keypath in keypaths:
                key = json.loads(keypath.read_text())["data"]
                if key_name in key or key_name in str(keypath):
                    return key
        except ValueError as e:
            logger.error(f"Key not found: {e}")

    async def get_sample_result(self):
        """
        Asynchronously retrieves a sample result from the AgentArtificial service.

        This function selects a random topic from the TOPICS list and creates a Message object
        with the topic as the content and role set to "user". It then sends a request to the
        AgentArtificial service with the topic message and retrieves the sample result. The
        sample result is logged as a debug message.

        The function then creates a Message object with the sample result as the content and
        role set to "user". The sample result is encoded using the embedding function from the
        tokenizer and returned along with the prompt Message object.

        Returns:
            Tuple[List[float], Message]: A tuple containing the encoded sample result and the
            prompt Message object.

        Raises:
            None
        """
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
        prompt = Message(content=str(sample_result), role="user")
        return tokenizer.embedding_function.encode(str(sample_result)), prompt

    def validate_input(self, embedding1, embedding2):
        """
        Calculate the cosine similarity between two embeddings.

        Args:
            embedding1 (List[int]): The first embedding.
            embedding2 (List[int]): The second embedding.

        Returns:
            float: The cosine similarity between the two embeddings.

        This function calculates the cosine similarity between two embeddings using the `tokenizer.cosine_similarity` method. It takes in two embeddings, `embedding1` and `embedding2`, as input and returns the cosine similarity between them. The cosine similarity is a measure of similarity between two vectors that is defined as the cosine of the angle between them. The angle is measured in radians and the cosine is a value between -1 and 1. A cosine similarity of 1 indicates that the two vectors are identical, while a cosine similarity of -1 indicates that the two vectors are opposite. The function logs the similarity result using the `logger.debug` method and returns the similarity value.
        """
        logger.info("\nevaluating sample similarity")
        result = tokenizer.cosine_similarity(
            embedding1=embedding1, embedding2=embedding2
        )
        logger.debug(f"\nsimilarity result: {result.hex()[:10]}...")
        return result

    def set_weights(self, uids, weights):
        """
        Set weights for validators.

        This function sets weights for validators using the provided `uids` and `weights` parameters. It reads the key information from the `VALI_KEY_FILEPATH` file, parses it, and extracts the `private_key` and `ss58_address` values. It then creates a `Keypair` object using the extracted values. Finally, it calls the `vote` method of the `c_client` object, passing in the `key`, `uids`, `weights`, and `netuid` parameters.

        Parameters:
            uids (List[int]): A list of validator IDs.
            weights (List[float]): A list of weights for the validators.

        Returns:
            None
        """
        with open(VALI_KEY_FILEPATH, "r", encoding="utf-8") as f:
            key = json.loads(f.read())["data"]

        private_key = json.loads(key)["private_key"]
        ss58_key = json.loads(key)["ss58_address"]

        key = Keypair(ss58_address=ss58_key, private_key=private_key)

        c_client.vote(key, uids, weights, netuid=10)

    async def validation_loop(self):
        """
        Asynchronously runs a validation loop that continuously checks the status of miners and their responses.

        This function does not take any parameters.

        The validation loop runs indefinitely and performs the following steps:
        1. Retrieves a sample result from the `get_sample_result` method.
        2. Extracts the length of the sample embedding and initializes a zero score list.
        3. Retrieves the `netuid` and address information from each miner in the `miner_list`.
        4. Makes a request to each miner to generate a response using the `make_request` method.
        5. Validates the input using the `validate_input` method and stores the scores in the `score_dict`.
        6. Adjusts the scores using the `threshold_sigmoid_reward_distribution` function.
        7. Calculates the total score and weighted scores.
        8. Sets the weights for each miner using the `set_weights` method.

        This function does not return any values.
        """
        logger.info("\nStarting validation loop")
        time.sleep(60)
        ss58address = ""
        while True:
            logger.info("\nGetting sample to compare...")
            sample_embedding, message = await self.get_sample_result()
            length = len(sample_embedding)
            zero_score = [0.00000000000000001 for _ in range(length)]
            score_dict = {}
            msg = message
            logger.info("\nQuerying miners...")
            try:
                self.miner_list = self.get_queryable_miners()  # type: ignore
            except Exception as e:
                logger.error(f"\nMiner list not found: {e}")

            logger.debug(f"\nChecking miners:\n {self.checking_list}")
            for miner_info in self.miner_list:
                print(miner_info)
                uid = miner_info["netuid"]  # type: ignore
                address_info = miner_info["address"]  # type: ignore
                miner_host = address_info[0]
                miner_port = address_info[1]
                miner_responses = {}

                try:
                    logger.info(f"\nMiner: {uid} - {miner_host}:{miner_port}")
                    miner_response = await self.make_request(
                        messages=[msg],
                        input_url=f"http://{miner_host}:{miner_port}/generate",
                    )
                    miner_responses[uid] = miner_response
                    logger.debug(f"\nMiner responses:\n {miner_responses}")

                except Exception as e:
                    logger.debug(f"\nMiner not found: {e}")
                    miner_responses[uid] = zero_score
            for uid, miner_response in miner_responses.items():
                try:
                    score = self.validate_input(
                        embedding1=miner_response, embedding2=sample_embedding
                    )
                    logger.debug(f"\nMiner: {uid}\nScore: {score}")

                    score_dict[uid] = score
                except ValueError as e:
                    logger.debug(f"\nScore not found: {e}")
                    score_dict[uid] = 0.00000000000000001

                logger.debug(f"\n Score: {score}.")

            logger.debug(f"\nScore dict:\n{score_dict}")
            adjusted_scores = threshold_sigmoid_reward_distribution(score_dict)
            logger.debug(f"\nAdjusted scores:\n{adjusted_scores}")
            total_scores: float | Literal[0] = sum(adjusted_scores.values())
            weighted_scores: dict[int, int] = {
                miner: int(score * 1000 / total_scores)
                for miner, score in adjusted_scores.items()
                if score != 0
            }

            if not weighted_scores:
                logger.info(
                    "\nNo effective weights found after adjustment. Please try again later."
                )

            logger.debug(f"\nFully adjusted scores:\n{adjusted_scores}")

            try:
                logger.info("voting on weighted scores")
                uids = list(weighted_scores.keys())
                weights = list(weighted_scores.values())
                print(uids, weights)
                self.set_weights(uids=uids, weights=weights)
            except Exception:
                logger.error("\nConnection error")

    async def serve(self) -> None:
        """
        Starts the validator server and handles validator tasks asynchronously.

        This function initializes a FastAPI application and adds CORS middleware to allow cross-origin requests.
        It then runs the application using the Uvicorn server.

        Parameters:
            self (Validator): The instance of the Validator class.

        Returns:
            None: This function does not return anything.
        """
        logger.info("starting validator server")

        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        uvicorn.run(app, host=self.host, port=self.port)
