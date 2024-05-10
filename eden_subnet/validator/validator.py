import random
from numpy import floating
from numpy._typing import _64Bit
from eden_subnet.base.base import BaseValidator, SampleInput
from eden_subnet.miner.config import Message
from eden_subnet.validator.config import ValidatorSettings, TOPICS
from eden_subnet.miner.tiktokenizer import TikTokenizer, TokenUsage
from eden_subnet.validator.sigmoid import threshold_sigmoid_reward_distribution
from communex.module.client import ModuleClient
from communex.types import Ss58Address
from communex.compat.key import Keypair
from communex.client import CommuneClient
from communex._common import get_node_url
from cellium.client import CelliumClient
from typing import Any, Generator, List, Union
from pathlib import Path
from loguru import logger
import json
from dotenv import load_dotenv

load_dotenv()

client = CelliumClient()
client.base_url = client.choose_base_url()
client.api_key = client.choose_api_key()


class Validator(BaseValidator):
    miner_list: list[tuple[str, Ss58Address]] = []
    c_client: Union[CommuneClient, None]
    checked_list: list[tuple[str, Ss58Address]] = []
    saved_key: Union[dict[Any, Any], None]
    checking_list: list[tuple[str, Ss58Address]] = []

    def __init__(self, config: ValidatorSettings) -> None:
        super().__init__(settings=config)
        self.tokenizer = TikTokenizer(
            kwargs=TokenUsage(prompt=0, total=0, request=0, response=0)
        )
        self.cellium = CelliumClient()
        self.c_client = CommuneClient(url=get_node_url(use_testnet=False))
        self.saved_key = json.loads(self.get_key(str(self.key_name)))  # type: ignore
        self.ss58_key = Ss58Address(self.settings.key_name)

    def get_message(self, topic) -> Message:
        test_prompt = f"please write a short alegory about the following topic: {topic}"
        return Message(content=test_prompt, role="user")

    def make_request(self, message: Message) -> str:
        responses: Generator[Any, Any, None] = self.cellium.generate(
            messages=[message.model_dump()]
        )

        return "".join(
            "\n".join(response["choices"][0]["content"]) for response in responses
        )

    def get_miner_by_netuid(self, miner_id: int):
        miners = self.get_queryable_miners()
        for miner, ss58 in miners:  # type: ignore
            if miner_id in miner:
                return ss58
            return

    def get_random_miner(self, miner_list: list):
        return random.choice(miner_list)

    def get_embedding(self, text_input: str) -> List[int]:
        return self.tokenizer.create_embedding(text=text_input)

    def evalutate_similarity(self, embedding1, embedding2) -> floating[_64Bit | Any]:
        return self.tokenizer.cosine_similarity(
            embedding1=embedding1, embedding2=embedding2
        )

    def get_key(self, key_name: str):
        try:
            key_path = Path("~/.commune/key").expanduser().resolve()
            keys = key_path.iterdir()
            for key in keys:
                if key_name in key.name:
                    return json.loads(key.read_text())["data"]
        except ValueError as e:
            logger.error(f"Key not found: {e}")

    def generate_sample_response(self, message: Message) -> str:
        self.cellium.api_key = self.cellium.choose_api_key()
        self.cellium.base_url = self.cellium.choose_base_url()
        self.cellium.model = self.cellium.choose_model()
        generated_generator = self.cellium.generate(messages=[message.model_dump()])
        return "".join(
            generated["choices"][0]["message"]["content"]
            for generated in generated_generator
        )

    def get_sample_result(self):
        topic = random.choice(TOPICS)
        prompt = self.get_message(topic)
        sample_result = self.generate_sample_response(prompt)
        sample_input = SampleInput(prompt=sample_result)
        return self.get_embedding(text_input=sample_result), sample_input

    def validate_input(self, miner_response, sample_embedding):
        return self.evalutate_similarity(sample_embedding, miner_response)

    def validation_loop(self):
        while True:
            sample_embedding, sample_input = self.get_sample_result()
            self.checked_list = []
            score_dict = {}
            for _ in range(25):
                miner = self.get_random_miner(self.miner_list)
                if miner not in self.checked_list:
                    if not miner:
                        self.checked_list = []
                        continue
                    self.checked_list.append(miner)
                    self.checking_list.append(miner)

                    miner_response = self.get_miner_generation(
                        miner_list=self.checking_list,  # type: ignore
                        miner_input=sample_input,
                    )

                    score = self.validate_input(
                        miner_response=miner_response, sample_embedding=sample_embedding
                    )
                    score_dict[miner] = score

            if not score_dict:
                print("No scores generated. Please try again later.")
                continue

            adjusted_scores = threshold_sigmoid_reward_distribution(score_dict)
            total_scores = sum(adjusted_scores.values())
            weighted_scores = {
                miner: int(score * 1000 / total_scores)
                for miner, score in adjusted_scores.items()
                if score != 0
            }

            if not weighted_scores:
                print(
                    "No effective weights found after adjustment. Please try again later."
                )
                continue

            try:
                uids = list(weighted_scores.keys())
                weights = list(weighted_scores.values())
                if self.c_client:
                    self.c_client.vote(
                        key=Keypair(ss58_address=self.settings.ss58_address),
                        uids=uids,
                        weights=weights,
                        netuid=self.netuid,
                    )
            except Exception as e:
                logger.error(e)

    async def serve(self) -> None:
        if self.saved_key:
            server = ModuleClient(
                host=self.settings.host,
                port=self.settings.port,
                key=Keypair(
                    ss58_address=self.settings.ss58_address,
                    ss58_format=self.saved_key["ss58_format"] or 42,
                ),
            )
        await server.call(fn="validation_loop", target_key=self.ss58_key, timeout=30)
