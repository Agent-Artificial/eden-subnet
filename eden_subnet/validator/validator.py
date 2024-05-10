import random
import json
import asyncio

from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
from typing import Any, Generator, List, Union
from numpy import floating
from numpy._typing import _64Bit
from cellium.client import CelliumClient
from communex.module.client import ModuleClient
from communex.types import Ss58Address
from communex.compat.key import Keypair
from communex.client import CommuneClient
from communex._common import get_node_url

from eden_subnet.base.base import BaseValidator, SampleInput
from eden_subnet.miner.config import Message
from eden_subnet.validator.config import ValidatorSettings, TOPICS
from eden_subnet.miner.tiktokenizer import TikTokenizer, TokenUsage
from eden_subnet.validator.sigmoid import threshold_sigmoid_reward_distribution

load_dotenv()

client = CelliumClient()
client.base_url = client.choose_base_url()
client.api_key = client.choose_api_key()


class Validator(BaseValidator):
    """
    A Validator class that orchestrates the validation of miners' responses against a standard sample using machine learning embeddings and similarity measures.
    This class integrates blockchain technology for secure and decentralized validation processes.

    Attributes:
        miner_list (list[tuple[str, Ss58Address]]): A list of miners identified by a tuple containing an identifier and an Ss58Address.
        c_client (Union[CommuneClient, None]): A client for communicating with a network node.
        checked_list (list[tuple[str, Ss58Address]]): A list to keep track of checked miners to avoid reevaluation within a loop.
        saved_key (Union[dict[Any, Any], None]): A dictionary holding the cryptographic key data.
        checking_list (list[tuple[str, Ss58Address]]): A list to temporarily store miners being currently evaluated.
    """

    miner_list: list[tuple[str, Ss58Address]] = []
    c_client: Union[CommuneClient, None]
    checked_list: list[tuple[str, Ss58Address]] = []
    saved_key: Union[dict[Any, Any], None]
    checking_list: list[tuple[str, Ss58Address]] = []

    def __init__(self, config: ValidatorSettings) -> None:
        """
        Initializes the Validator with specific settings and prepares the environment for validation tasks.

        Args:
            config (ValidatorSettings): Configuration settings for the validator.
        """
        logger.info(f"Initializing validator with settings: {config.model_dump()}")
        super().__init__(settings=config)
        self.tokenizer = TikTokenizer(
            kwargs=TokenUsage(prompt=0, total=0, request=0, response=0)
        )
        self.cellium = CelliumClient()
        self.c_client = CommuneClient(url=get_node_url(use_testnet=False))
        self.saved_key = json.loads(self.get_key(str(self.key_name)))  # type: ignore
        self.ss58_key = Ss58Address(self.settings.key_name)

    def get_message(self, topic) -> Message:
        """
        Generates a Message object with a content prompt based on a given topic.

        Args:
            topic (str): The topic for which to generate the prompt.

        Returns:
            Message: A message object containing the generated prompt.
        """
        logger.info("generating test prompt")
        test_prompt = f"please write a short alegory about the following topic: {topic}"
        return Message(content=test_prompt, role="user")

    def make_request(self, message: Message) -> str:
        """
        Makes a request to generate responses based on the provided message.

        Args:
            message (Message): The message object containing the prompt.

        Returns:
            str: The concatenated string of responses.
        """
        logger.info("making sample request")
        responses: Generator[Any, Any, None] = self.cellium.generate(
            messages=[message.model_dump()]
        )

        return "".join(
            "\n".join(response["choices"][0]["content"]) for response in responses
        )

    def get_miner_by_netuid(self, miner_id: int):
        """
        Retrieves a miner's Ss58 address based on their network user ID.

        Args:
            miner_id (int): The network user ID of the miner.

        Returns:
            Ss58Address or None: The Ss58Address of the miner if found, otherwise None.
        """
        logger.info("getting miner by netuid")
        miners = self.get_queryable_miners()
        for miner, ss58 in miners:  # type: ignore
            if miner_id in miner:
                return ss58
            return

    def get_random_miner(self, miner_list: list):
        """
        Selects a random miner from the provided list of miners.

        Args:
            miner_list (list): A list of miners from which to select.

        Returns:
            tuple[str, Ss58Address]: A randomly selected miner.
        """
        logger.info("getting random miner")
        return random.choice(miner_list)

    def get_embedding(self, text_input: str) -> List[int]:
        """
        Generates an embedding for the given text input using the tokenizer.

        Args:
            text_input (str): The input text to convert into an embedding.

        Returns:
            List[int]: A list of integers representing the embedding of the input text.
        """
        logger.info("getting sample embedding")
        return self.tokenizer.create_embedding(text=text_input)

    def evalutate_similarity(self, embedding1, embedding2) -> floating[_64Bit | Any]:
        """
        Evaluates the cosine similarity between two embeddings.

        Args:
            embedding1 (List[int]): The first embedding vector.
            embedding2 (List[int]): The second embedding vector.

        Returns:
            floating: The computed similarity score between the two embeddings.
        """
        logger.info("evaluating sample similarity")
        result = self.tokenizer.cosine_similarity(
            embedding1=embedding1, embedding2=embedding2
        )
        logger.debug(f"similarity result: {result.hex()[:10]}...")
        return result

    def get_key(self, key_name: str):
        """
        Retrieves the cryptographic key data from local storage based on the provided key name.

        Args:
            key_name (str): The name of the key to retrieve.

        Returns:
            dict or None: The key data if found, otherwise None.
        """
        logger.info("getting validator key from local storage")
        try:
            key_path = Path("~/.commune/key").expanduser().resolve()
            keys = key_path.iterdir()
            for key in keys:
                if key_name in key.name:
                    return json.loads(key.read_text())["data"]
        except ValueError as e:
            logger.error(f"Key not found: {e}")

    def generate_sample_response(self, message: Message) -> str:
        """
        Generates a sample response for a given message.

        Args:
            message (Message): The message for which to generate a response.

        Returns:
            str: The generated response.
        """
        logger.info("generating sample response")
        self.cellium.api_key = self.cellium.choose_api_key()
        self.cellium.base_url = self.cellium.choose_base_url()
        self.cellium.model = self.cellium.choose_model()
        response = self.make_request(message)
        logger.debug(f"sample response generated:\n{response}")
        return response

    def get_sample_result(self):
        """
        Retrieves a sample result based on a randomly chosen topic.

        Returns:
            tuple[List[int], SampleInput]: A tuple containing the embedding of the sample result and the SampleInput object.
        """
        logger.info("getting sample result")
        topic = random.choice(TOPICS)
        logger.debug(f"sample topic:\n{topic}")
        prompt = self.get_message(topic)
        sample_result = self.generate_sample_response(prompt)
        sample_input = SampleInput(prompt=sample_result)
        return self.get_embedding(text_input=sample_result), sample_input

    def validate_input(self, miner_response, sample_embedding):
        """
        Validates the miner response against the sample embedding.

        Args:
            miner_response (List[int]): The embedding of the miner's response.
            sample_embedding (List[int]): The embedding of the sample input.

        Returns:
            floating: The similarity score between the miner response and the sample embedding.
        """
        logger.info("validating miner response vs sample input")
        similarity = self.evalutate_similarity(sample_embedding, miner_response)
        logger.debug(f"similiarity: {similarity}")
        return similarity

    def validation_loop(self):
        """
        Executes the validation loop, continuously validating miners' responses and updating scores.
        """
        logger.info("starting validation loop")
        while True:
            sample_embedding, sample_input = self.get_sample_result()
            self.checked_list = []
            score_dict = {}
            for _ in range(25):
                miner = self.get_random_miner(self.miner_list)
                if miner not in self.checked_list:
                    if not miner:
                        self.checked_list = []
                        logger.info("No miner found. Please try again later.")
                        continue
                    self.checked_list.append(miner)
                    self.checking_list.append(miner)

                    miner_response = self.get_miner_generation(
                        miner_list=self.checking_list,  # type: ignore
                        miner_input=sample_input,
                    )
                    if not miner_response:
                        print("No miner response found. Please try again later.")

                    score = self.validate_input(
                        miner_response=miner_response, sample_embedding=sample_embedding
                    )
                    score_dict[miner] = score

            if not score_dict:
                logger.info("No scores generated. Please try again later.")
                continue

            adjusted_scores = threshold_sigmoid_reward_distribution(score_dict)
            total_scores = sum(adjusted_scores.values())
            weighted_scores = {
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
        """
        Starts the server and handles validator tasks asynchronously.
        """
        logger.info("starting validator server")
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


if __name__ == "__main__":
    settings = ValidatorSettings(
        key_name="agent.ArtificialValidator",
        module_path="agent.ArtificialValidator",
        host="0.0.0.0",
        port=50050,
        use_testnet=True,
    )
    validator = Validator(settings)
    asyncio.run(validator.serve())
