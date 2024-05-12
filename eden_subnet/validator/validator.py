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
from typing import Any, Literal, List, Union
from numpy import floating
from numpy._typing import _64Bit
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from cellium.client import CelliumClient
from communex.module.client import ModuleClient
from communex.types import Ss58Address
from communex.compat.key import Keypair
from communex.client import CommuneClient
from communex._common import get_node_url
from pydantic import ConfigDict, Field
from eden_subnet.base.base import BaseValidator, Message
from eden_subnet.miner.config import Message
from eden_subnet.validator.config import ValidatorSettings, TOPICS
from eden_subnet.miner.tiktokenizer import TikTokenizer
from eden_subnet.validator.sigmoid import threshold_sigmoid_reward_distribution
from dotenv import load_dotenv

load_dotenv()


c_client = CommuneClient(get_node_url())

tokenizer = TikTokenizer()


class Validator(BaseValidator):
    key_name: str = Field(default="")
    module_path: str = Field(default="")
    host: str = Field(default="")
    port: int = Field(default=0)
    miner_list: list[tuple[str, Ss58Address]] = Field(default=[])
    checked_list: list[tuple[str, Ss58Address]] = Field(default=[])
    saved_key: Union[dict[Any, Any], None] = Field(default=None)
    checking_list: list[tuple[str, Ss58Address]] = Field(default=[])
    ss58_address: Ss58Address = Field(default_factory=None)
    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)
    settings: ValidatorSettings = Field(default_factory=ValidatorSettings)
    __pydantic_fields_set__ = {
        "key_name",
        "module_path",
        "host",
        "port",
        "miner_list",
        "checked_list",
        "saved_key",
        "checking_list",
        "settings",
    }

    def __init__(self, settings: ValidatorSettings) -> None:
        logger.info(f"Initializing validator with settings: {settings.model_dump()}")
        super().__init__(config=settings)
        self.key_name = settings.key_name
        self.module_path = settings.module_path
        self.host = settings.host
        self.port = settings.port
        self.saved_key = json.loads(self.get_key(str(self.key_name)))  # type: ignore
        self.ss58_address = Ss58Address(self.settings.key_name)
        self.miner_list = []
        self.checked_list = []
        self.checking_list = []

    async def make_request(self, message: Message) -> str:
        import requests
        import json

        url = str(os.getenv("AGENTARTIFICIAL_URL"))
        payload = json.dumps(
            {
                "messages": [message.model_dump()],
                "model": str(os.getenv("AGENTARTIFICIAL_MODEL")),
            }
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": str(os.getenv("AGENTARTIFICIAL_API_KEY")),
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()["choices"][0]["message"]["content"]

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

    async def generate_sample_response(self, message: Message) -> str:
        logger.info("generating sample response")
        response = await self.make_request(message)
        logger.debug(f"sample response generated:\n{response}")
        return response

    async def get_sample_result(self):
        logger.info("getting sample result")
        topic = random.choice(TOPICS)
        logger.debug(f"sample topic:\n{topic}")
        prompt = Message(content=topic, role="user")
        sample_result = await self.generate_sample_response(message=prompt)
        return tokenizer.embedding_function.encode(sample_result), prompt

    def validate_input(self, embedding1, embedding2):
        logger.info("evaluating sample similarity")
        result = tokenizer.cosine_similarity(
            embedding1=embedding1, embedding2=embedding2
        )
        logger.debug(f"similarity result: {result.hex()[:10]}...")
        return result

    async def validation_loop(self):
        logger.info("\nStarting validation loop")
        while True:
            # time.sleep(60)
            sample_embedding, message = await self.get_sample_result()
            length = len(sample_embedding)
            zero_score = [0.0001 for _ in range(length)]
            self.checked_list = []
            self.checking_list = []
            score_dict = {}
            try:
                self.miner_list = self.get_queryable_miners()  # type: ignore
            except Exception as e:
                logger.error(f"\nMiner list not found: {e}")
                continue

            if len(self.miner_list) > 0 and len(self.miner_list) <= 25:
                check_range = len(self.miner_list)
                logger.debug(check_range)
                if len(self.miner_list) <= 0:
                    logger.error("\nNo miner found. Please try again later.")
                    continue
            else:
                check_range = 25

            for _ in range(check_range):
                try:
                    miner = random.choice(self.miner_list)
                except (IndexError, KeyError) as e:
                    logger.error(f"\nNo miner found. Please try again later. {e}")
                    continue

                uid, address = miner

                if miner not in self.checked_list:
                    self.checked_list.append(miner)
                    self.checking_list.append(miner)

            logger.debug(f"\nChecking miners:\n {self.checking_list}")
            miner_responses = {}
            try:
                miner_responses = self.get_miner_generation(
                    miner_list=self.checking_list,  # type: ignore
                    miner_input=message,
                )
                logger.debug(f"\nMiner response: {miner_responses}")
            except Exception as e:
                logger.error(f"\nError getting miner reponses: {e}")
            for uid, miner_response in miner_responses.items():
                try:
                    score = self.validate_input(
                        embedding1=miner_response, embedding2=sample_embedding
                    )

                    score_dict[uid] = score
                except ValueError as e:
                    logger.error(f"\nScore not found: {e}")
                    score_dict[uid] = 0.0001

            if not score_dict:
                logger.error("\nNo scores generated. Please try again later.")
                continue

            adjusted_scores: dict[int, float] = threshold_sigmoid_reward_distribution(
                score_dict
            )
            total_scores: float | Literal[0] = sum(adjusted_scores.values())
            weighted_scores: dict[int, int] = {
                miner: int(score * 1000 / total_scores)
                for miner, score in adjusted_scores.items()
                if score != 0
            }

            if not weighted_scores:
                logger.info(
                    "No effective weights found after adjustment. Please try again later."
                )
                continue
            logger.debug(f"adjusted scores:\n{adjusted_scores}")

            try:
                logger.info("voting on weighted scores")
                uids = list(weighted_scores.keys())
                weights = list(weighted_scores.values())
                if c_client:
                    c_client.vote(
                        key=Keypair(ss58_address=self.settings.ss58_address),
                        uids=uids,
                        weights=weights,
                        netuid=10,
                    )
            except ConnectionError as e:
                logger.error(e)

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


if __name__ == "__main__":
    settings = ValidatorSettings(
        key_name="agent.ArtificialValidator",
        module_path="agent.ArtificialValidator",
        host="0.0.0.0",
        port=50050,
        use_testnet=True,
    )
    validator = Validator(settings)
    asyncio.run(validator.validation_loop())
