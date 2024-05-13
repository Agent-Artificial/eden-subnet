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
    address: str  # Example field, adjust as needed


class ConfigDict(BaseModel):
    arbitrary_types_allowed: bool = True


class ValidatorSettings(BaseModel):
    key_name: str
    module_path: str
    host: str
    port: int
    # Add other settings as needed


class BaseValidator(BaseModel):
    # Assuming BaseValidator needs these four properties
    key_name: str
    module_path: str
    host: str
    port: int


class Validator(BaseValidator):
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
        # Call the initializer of BaseValidator with required positional arguments
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
        logger.info("getting miner by netuid")
        miners = self.get_queryable_miners()
        for miner, ss58 in miners:  # type: ignore
            if miner_id in miner:
                return ss58
            return

    def get_key(self, key_name: str):
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
        logger.info("\nevaluating sample similarity")
        result = tokenizer.cosine_similarity(
            embedding1=embedding1, embedding2=embedding2
        )
        logger.debug(f"\nsimilarity result: {result.hex()[:10]}...")
        return result

    def set_weights(self, uids, weights):
        with open(VALI_KEY_FILEPATH, "r", encoding="utf-8") as f:
            key = json.loads(f.read())["data"]

        private_key = json.loads(key)["private_key"]
        ss58_key = json.loads(key)["ss58_address"]

        key = Keypair(ss58_address=ss58_key, private_key=private_key)

        c_client.vote(key, uids, weights, netuid=10)

    async def validation_loop(self):
        logger.info("\nStarting validation loop")
        while True:
            # time.sleep(60)
            ss58address = ""
            sample_embedding, message = await self.get_sample_result()
            length = len(sample_embedding)
            zero_score = [0.0001 for _ in range(length)]
            score_dict = {}
            msg = message
            try:
                self.miner_list = self.get_queryable_miners()  # type: ignore
            except Exception as e:
                logger.error(f"\nMiner list not found: {e}")

            for miner_info in self.miner_list:
                print(miner_info)
                uid = miner_info["netuid"]
                address_info = miner_info["address"]
                miner_host = address_info[0]
                miner_port = address_info[1]
                miner_responses = {}
                logger.debug(f"\nChecking miners:\n {self.checking_list}")
                try:
                    logger.debug(f"\nMiner: {uid} - {miner_host}:{miner_port}")
                    miner_response = await self.make_request(
                        messages=[msg],
                        input_url=f"http://{miner_host}:{miner_port}/generate",
                    )
                    miner_responses[uid] = miner_response
                    logger.debug(f"\nMiner responses:\n {miner_responses}")
                    miner_responses[uid] = zero_score
                except Exception as e:
                    logger.error(f"\nMiner not found: {e}")
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
        Starts the server and handles validator tasks asynchronously.
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

        #        @app.post("/register")
        #        def register(request: Request):
        #            data = request.json()
        #            self.miner_list.append(data["address"])
        #            if not data:
        #                raise HTTPException(status_code=400, detail="No data received")
        #
        #        await self.validation_loop()
        uvicorn.run(app, host=self.host, port=self.port)
